"""
互動數據去重和批量抓取 API
"""

import json
import os
import asyncio
import sys
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks
import logging

# 添加專案根目錄到 Python 路徑
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

logger = logging.getLogger(__name__)

# 創建路由器
router = APIRouter(prefix="/interactions", tags=["interactions"])

# 導入全局服務實例
post_record_service = None

def get_post_record_service():
    global post_record_service
    if post_record_service is None:
        try:
            from postgresql_service import PostgreSQLPostRecordService
            post_record_service = PostgreSQLPostRecordService()
        except Exception as e:
            logger.error(f"❌ PostgreSQL 服務初始化失敗: {e}")
            return None
    return post_record_service

def load_external_posts_data() -> Dict[str, Any]:
    """載入外部貼文數據"""
    try:
        external_data_file = "processed_external_posts.json"
        if os.path.exists(external_data_file):
            with open(external_data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # 處理不同的數據格式
                if isinstance(data, list):
                    # 如果是數組格式
                    return {"posts": data, "kol_stats": {}, "total_posts": len(data)}
                elif isinstance(data, dict):
                    # 如果是對象格式
                    return data
                else:
                    logger.warning("⚠️ 外部貼文數據格式不正確")
                    return {"posts": [], "kol_stats": {}, "total_posts": 0}
        else:
            logger.warning("⚠️ 外部貼文數據文件不存在")
            return {"posts": [], "kol_stats": {}, "total_posts": 0}
    except Exception as e:
        logger.error(f"❌ 載入外部貼文數據失敗: {e}")
        return {"posts": [], "kol_stats": {}, "total_posts": 0}

async def get_kol_credentials_from_db(kol_serial: int):
    """從 KOL SQL 數據庫獲取憑證"""
    try:
        from kol_database_service import kol_db_service
        
        kol_data = kol_db_service.get_kol_by_serial(str(kol_serial))
        
        if not kol_data:
            logger.warning(f"⚠️ 找不到 KOL-{kol_serial} 的數據")
            return None
            
        # 導入 LoginCredentials
        try:
            from src.clients.cmoney.cmoney_client import LoginCredentials
        except ImportError:
            logger.error("❌ 無法導入 LoginCredentials")
            return None
        
        credentials = LoginCredentials(
            email=kol_data.email,
            password=kol_data.password
        )
        
        logger.info(f"✅ 從數據庫獲取 KOL-{kol_serial} 憑證成功")
        return credentials
        
    except Exception as e:
        logger.error(f"❌ 從數據庫獲取 KOL-{kol_serial} 憑證失敗: {e}")
        return None

async def get_kol_credentials_fallback(kol_serial: int):
    """硬編碼 KOL 憑證回退函數"""
    try:
        try:
            from src.clients.cmoney.cmoney_client import LoginCredentials
        except ImportError:
            logger.error("❌ 無法導入 LoginCredentials")
            return None
        
        # 從環境變數獲取 KOL 憑證
        import os
        kol_email = os.getenv(f'KOL_{kol_serial}_EMAIL')
        kol_password = os.getenv(f'KOL_{kol_serial}_PASSWORD')
        
        if kol_email and kol_password:
            credentials = LoginCredentials(email=kol_email, password=kol_password)
            logger.info(f"✅ 從環境變數獲取 KOL-{kol_serial} 憑證")
            return credentials
        else:
            logger.warning(f"⚠️ 環境變數中找不到 KOL-{kol_serial} 的憑證")
            # 嘗試使用預設 KOL 憑證
            default_email = os.getenv('DEFAULT_KOL_EMAIL')
            default_password = os.getenv('DEFAULT_KOL_PASSWORD')
            
            if default_email and default_password:
                return LoginCredentials(email=default_email, password=default_password)
            else:
                logger.error(f"❌ 環境變數中找不到預設 KOL 憑證")
                return None
                
    except Exception as e:
        logger.error(f"❌ 從環境變數獲取 KOL 憑證失敗: {e}")
        return None

@router.post("/deduplicate")
async def deduplicate_posts():
    """去重功能：刪除重複的 article_id"""
    
    try:
        logger.info("🔄 開始執行去重操作...")
        
        # 獲取所有貼文（系統 + 外部）
        system_posts = []
        if get_post_record_service():
            published_posts = get_post_record_service().get_all_posts(status='published')
            system_posts = [
                {
                    "post_id": post.post_id,
                    "article_id": post.cmoney_post_id,
                    "kol_serial": post.kol_serial,
                    "source": "system"
                }
                for post in published_posts if post.cmoney_post_id
            ]
        
        external_data = load_external_posts_data()
        external_posts = [
            {
                "post_id": post["post_id"],
                "article_id": post["article_id"],
                "kol_serial": post["kol_serial"],
                "source": "external"
            }
            for post in external_data.get("posts", [])
        ]
        
        all_posts = system_posts + external_posts
        
        # 統計 article_id 出現次數
        article_id_count = {}
        for post in all_posts:
            article_id = post["article_id"]
            if article_id not in article_id_count:
                article_id_count[article_id] = []
            article_id_count[article_id].append(post)
        
        # 找出重複的 article_id
        duplicates = {aid: posts for aid, posts in article_id_count.items() if len(posts) > 1}
        
        # 去重策略：保留系統發文，刪除外部重複
        removed_count = 0
        duplicate_details = []
        
        for article_id, posts in duplicates.items():
            system_posts_for_article = [p for p in posts if p["source"] == "system"]
            external_posts_for_article = [p for p in posts if p["source"] == "external"]
            
            if system_posts_for_article and external_posts_for_article:
                # 如果有系統發文，保留系統發文，刪除外部重複
                for external_post in external_posts_for_article:
                    duplicate_details.append({
                        "article_id": article_id,
                        "removed_post_id": external_post["post_id"],
                        "removed_source": "external",
                        "kept_post_id": system_posts_for_article[0]["post_id"],
                        "kept_source": "system"
                    })
                    removed_count += 1
            elif len(external_posts_for_article) > 1:
                # 如果只有外部發文，保留第一個，刪除其他
                kept_post = external_posts_for_article[0]
                for external_post in external_posts_for_article[1:]:
                    duplicate_details.append({
                        "article_id": article_id,
                        "removed_post_id": external_post["post_id"],
                        "removed_source": "external",
                        "kept_post_id": kept_post["post_id"],
                        "kept_source": "external"
                    })
                    removed_count += 1
        
        logger.info(f"✅ 去重完成 - 發現 {len(duplicates)} 個重複 article_id，移除 {removed_count} 個重複記錄")
        
        return {
            "success": True,
            "message": f"去重完成 - 發現 {len(duplicates)} 個重複 article_id，移除 {removed_count} 個重複記錄",
            "duplicate_count": len(duplicates),
            "removed_count": removed_count,
            "duplicate_details": duplicate_details,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ 去重操作失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=f"去重操作失敗: {str(e)}")

@router.post("/fetch-all-interactions")
async def fetch_all_interactions(background_tasks: BackgroundTasks):
    """一鍵抓取所有過往互動數據"""
    
    try:
        logger.info("🔄 開始一鍵抓取所有過往互動數據...")
        
        # 獲取所有貼文（系統 + 外部）
        system_posts = []
        if get_post_record_service():
            published_posts = get_post_record_service().get_all_posts(status='published')
            system_posts = [
                {
                    "post_id": post.post_id,
                    "article_id": post.cmoney_post_id,
                    "kol_serial": post.kol_serial,
                    "source": "system"
                }
                for post in published_posts if post.cmoney_post_id
            ]
        
        external_data = load_external_posts_data()
        external_posts = [
            {
                "post_id": post["post_id"],
                "article_id": post["article_id"],
                "kol_serial": post["kol_serial"],
                "source": "external"
            }
            for post in external_data.get("posts", [])
        ]
        
        all_posts = system_posts + external_posts
        total_posts = len(all_posts)
        
        logger.info(f"📊 找到 {total_posts} 篇貼文需要抓取互動數據")
        
        # 在背景任務中執行抓取
        background_tasks.add_task(fetch_interactions_background, all_posts)
        
        return {
            "success": True,
            "message": f"已開始抓取 {total_posts} 篇貼文的互動數據，請稍後查看結果",
            "total_posts": total_posts,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ 一鍵抓取失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=f"一鍵抓取失敗: {str(e)}")

async def fetch_interactions_background(all_posts: List[Dict[str, Any]]):
    """背景任務：抓取所有貼文的互動數據"""
    
    logger.info(f"🔄 背景任務開始抓取 {len(all_posts)} 篇貼文的互動數據")
    
    success_count = 0
    failed_count = 0
    results = []
    
    for i, post in enumerate(all_posts, 1):
        try:
            logger.info(f"📊 處理第 {i}/{len(all_posts)} 篇貼文: {post['article_id']}")
            
            # 調用互動數據獲取函數
            from routes.interaction_routes import get_cmoney_interaction_data
            
            interaction_data = await get_cmoney_interaction_data(
                post["article_id"], 
                post["kol_serial"]
            )
            
            if interaction_data:
                result = {
                    "post_id": post["post_id"],
                    "article_id": post["article_id"],
                    "kol_serial": post["kol_serial"],
                    "source": post["source"],
                    "interaction_data": interaction_data,
                    "status": "success"
                }
                
                # 更新數據
                if post["source"] == "system" and get_post_record_service():
                    # 系統貼文：更新數據庫
                    update_data = {
                        'views': interaction_data.get('views', 0),
                        'likes': interaction_data.get('likes', 0),
                        'comments': interaction_data.get('comments', 0),
                        'shares': interaction_data.get('shares', 0),
                        'updated_at': datetime.now()
                    }
                    
                    get_post_record_service().update_post_record(post["post_id"], update_data)
                    logger.info(f"✅ 系統貼文數據已更新到數據庫 - {post['article_id']}")
                    
                elif post["source"] == "external":
                    # 外部貼文：更新 JSON 文件
                    try:
                        external_data = load_external_posts_data()
                        posts = external_data.get("posts", [])
                        
                        # 找到對應的外部貼文並更新
                        for j, ext_post in enumerate(posts):
                            if ext_post.get("post_id") == post["post_id"]:
                                posts[j].update({
                                    'views': interaction_data.get('views', 0),
                                    'likes': interaction_data.get('likes', 0),
                                    'comments': interaction_data.get('comments', 0),
                                    'shares': interaction_data.get('shares', 0),
                                    'bookmarks': interaction_data.get('bookmarks', 0),
                                    'donations': interaction_data.get('donations', 0),
                                    'updated_at': datetime.now().isoformat()
                                })
                                break
                        
                        # 保存更新後的數據
                        external_data["posts"] = posts
                        with open("processed_external_posts.json", 'w', encoding='utf-8') as f:
                            json.dump(external_data, f, ensure_ascii=False, indent=2)
                        
                        logger.info(f"✅ 外部貼文數據已更新到文件 - {post['article_id']}")
                        
                    except Exception as e:
                        logger.error(f"❌ 更新外部貼文數據失敗 - {post['article_id']}: {e}")
                
                success_count += 1
                logger.info(f"✅ 成功抓取 - {post['article_id']}: {interaction_data}")
            else:
                result = {
                    "post_id": post["post_id"],
                    "article_id": post["article_id"],
                    "kol_serial": post["kol_serial"],
                    "source": post["source"],
                    "status": "failed",
                    "error": "無法獲取互動數據"
                }
                failed_count += 1
                logger.warning(f"⚠️ 抓取失敗 - {post['article_id']}")
            
            results.append(result)
            
            # 避免請求過於頻繁
            await asyncio.sleep(0.5)
            
        except Exception as e:
            logger.error(f"❌ 抓取貼文 {post['article_id']} 失敗: {str(e)}")
            failed_count += 1
            results.append({
                "post_id": post["post_id"],
                "article_id": post["article_id"],
                "kol_serial": post["kol_serial"],
                "source": post["source"],
                "status": "error",
                "error": str(e)
            })
    
    logger.info(f"✅ 背景任務完成 - 成功: {success_count}, 失敗: {failed_count}")
    
    # 保存結果到文件
    result_file = f"interaction_fetch_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump({
            "summary": {
                "total_posts": len(all_posts),
                "success_count": success_count,
                "failed_count": failed_count,
                "timestamp": datetime.now().isoformat()
            },
            "results": results
        }, f, ensure_ascii=False, indent=2)
    
    logger.info(f"💾 抓取結果已保存到: {result_file}")

@router.post("/refresh-all")
async def refresh_all_interactions():
    """批量刷新所有貼文的互動數據（改進版）"""
    
    try:
        logger.info("🔄 開始批量刷新所有貼文的互動數據...")
        
        # 先執行去重
        deduplicate_result = await deduplicate_posts()
        
        # 再執行一鍵抓取
        fetch_result = await fetch_all_interactions(BackgroundTasks())
        
        return {
            "success": True,
            "message": "批量刷新完成 - 已去重並抓取最新互動數據",
            "deduplicate": deduplicate_result,
            "fetch": fetch_result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ 批量刷新失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=f"批量刷新失敗: {str(e)}")

@router.get("/stats")
async def get_interaction_stats():
    """獲取互動數據統計"""
    try:
        post_service = get_post_record_service()
        if not post_service:
            raise HTTPException(status_code=500, detail="數據庫服務不可用")
        
        all_posts = post_service.get_all_posts(limit=10000)
        
        total_posts = len(all_posts)
        posts_with_interactions = sum(1 for post in all_posts if post.get('likes', 0) > 0 or post.get('views', 0) > 0)
        
        total_views = sum(post.get('views', 0) for post in all_posts)
        total_likes = sum(post.get('likes', 0) for post in all_posts)
        total_comments = sum(post.get('comments', 0) for post in all_posts)
        total_shares = sum(post.get('shares', 0) for post in all_posts)
        
        return {
            "total_posts": total_posts,
            "posts_with_interactions": posts_with_interactions,
            "interaction_coverage": round(posts_with_interactions / total_posts * 100, 2) if total_posts > 0 else 0,
            "total_views": total_views,
            "total_likes": total_likes,
            "total_comments": total_comments,
            "total_shares": total_shares,
            "total_engagement": total_likes + total_comments + total_shares
        }
        
    except Exception as e:
        logger.error(f"❌ 獲取互動數據統計失敗: {e}")
        raise HTTPException(status_code=500, detail=f"統計失敗: {str(e)}")