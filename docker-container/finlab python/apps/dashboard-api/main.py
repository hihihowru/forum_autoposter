"""
Dashboard API 服務
提供三張儀表板的數據 API
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import os
import sys

# 添加專案根目錄到 Python 路徑
sys.path.append('./src')
sys.path.append('../../../../src')

# Google Sheets 已棄用，只使用 posting-service 數據

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 創建 FastAPI 應用
app = FastAPI(
    title="Dashboard API",
    description="虛擬 KOL 系統儀表板 API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 添加 CORS 中間件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生產環境應該限制特定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Google Sheets 已棄用，創建替換函數避免錯誤
def get_sheets_client():
    """Google Sheets 已棄用，返回 None"""
    logger.warning("⚠️ Google Sheets 已棄用，此功能不再可用")
    return None

@app.get("/")
async def root():
    """根路徑"""
    return {
        "message": "Dashboard API 服務運行中",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "system_monitoring": "/api/dashboard/system-monitoring",
            "content_management": "/api/dashboard/content-management", 
            "interaction_analysis": "/api/dashboard/interaction-analysis"
        }
    }

@app.get("/health")
async def health_check():
    """健康檢查"""
    try:
        client = get_sheets_client()
        # 測試 Google Sheets 連接
        client.read_sheet('同學會帳號管理', 'A1:Z1')
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "google_sheets": "connected",
                "database": "ready"
            }
        }
    except Exception as e:
        logger.error(f"健康檢查失敗: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
        )

# ==================== 系統監控儀表板 ====================

@app.get("/api/dashboard/system-monitoring")
async def get_system_monitoring_data():
    """
    獲取系統監控儀表板數據
    包括微服務狀態、任務執行狀態、系統資源使用等
    """
    try:
        client = get_sheets_client()
        
        # 獲取 KOL 帳號管理數據
        kol_data = client.read_sheet('同學會帳號管理', 'A:AZ')
        kol_headers = kol_data[0] if kol_data else []
        kol_records = kol_data[1:] if len(kol_data) > 1 else []
        
        # 獲取貼文記錄數據
        post_data = client.read_sheet('貼文記錄表', 'A:R')
        post_headers = post_data[0] if post_data else []
        post_records = post_data[1:] if len(post_data) > 1 else []
        
        # 統計數據
        total_kols = len(kol_records)
        active_kols = len([k for k in kol_records if len(k) > 10 and k[10] == '啟用'])
        total_posts = len(post_records)
        published_posts = len([p for p in post_records if len(p) > 11 and p[11] == '已發布'])
        
        # 模擬微服務狀態 (實際應該從各微服務獲取)
        microservices_status = {
            "ohlc_api": {"status": "healthy", "uptime": "99.9%", "response_time": "120ms"},
            "analyze_api": {"status": "healthy", "uptime": "99.8%", "response_time": "250ms"},
            "summary_api": {"status": "healthy", "uptime": "99.7%", "response_time": "180ms"},
            "trending_api": {"status": "healthy", "uptime": "99.9%", "response_time": "90ms"},
            "posting_service": {"status": "healthy", "uptime": "99.6%", "response_time": "300ms"},
            "trainer": {"status": "healthy", "uptime": "99.5%", "response_time": "500ms"}
        }
        
        # 任務執行統計
        task_stats = {
            "hourly_tasks": {"success": 95, "failed": 5, "total": 100},
            "daily_tasks": {"success": 98, "failed": 2, "total": 100},
            "weekly_tasks": {"success": 100, "failed": 0, "total": 100}
        }
        
        return {
            "timestamp": datetime.now().isoformat(),
            "system_overview": {
                "total_kols": total_kols,
                "active_kols": active_kols,
                "total_posts": total_posts,
                "published_posts": published_posts,
                "success_rate": round((published_posts / total_posts * 100) if total_posts > 0 else 0, 2)
            },
            "microservices": microservices_status,
            "task_execution": task_stats,
            "data_sources": {
                "google_sheets": "connected",
                "cmoney_api": "not_connected",  # 暫時未連接
                "finlab_api": "not_connected"   # 暫時未連接
            }
        }
        
    except Exception as e:
        logger.error(f"獲取系統監控數據失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取系統監控數據失敗: {str(e)}")

# ==================== 內容管理儀表板 ====================

@app.get("/api/dashboard/content-management")
async def get_content_management_data():
    """
    獲取內容管理儀表板數據
    包括 KOL 列表、文章列表、內容生成統計等
    """
    try:
        # 從 posting-service 獲取貼文數據
        import httpx
        posting_service_url = os.getenv("POSTING_SERVICE_URL", "http://posting-service:8000")
        post_records = []
        
        try:
            async with httpx.AsyncClient() as http_client:
                response = await http_client.get(f"{posting_service_url}/posts/", timeout=30.0)
                if response.status_code == 200:
                    posting_data = response.json()
                    post_records = posting_data.get("posts", [])
                    logger.info(f"✅ 從 posting-service 獲取到 {len(post_records)} 篇貼文")
                else:
                    logger.error(f"❌ posting-service 響應錯誤: {response.status_code}")
                    post_records = []
        except Exception as e:
            logger.error(f"❌ 無法從 posting-service 獲取數據: {e}")
            post_records = []
        
        # 從 posting-service 獲取 KOL 數據
        try:
            async with httpx.AsyncClient() as http_client:
                response = await http_client.get(f"{posting_service_url}/posts/kol-list", timeout=30.0)
                if response.status_code == 200:
                    kol_data = response.json()
                    kol_records = kol_data if isinstance(kol_data, list) else []
                    logger.info(f"✅ 從 posting-service 獲取到 {len(kol_records)} 個 KOL")
                else:
                    logger.error(f"❌ posting-service KOL 響應錯誤: {response.status_code}")
                    kol_records = []
        except Exception as e:
            logger.error(f"❌ 無法從 posting-service 獲取 KOL 數據: {e}")
            kol_records = []
        
        # 處理 KOL 數據
        kol_list = []
        for record in kol_records:
            # 從 posting-service 獲取的 KOL 數據格式
            if isinstance(record, dict):
                kol_info = {
                    "serial": record.get("serial", ""),
                    "nickname": record.get("nickname", ""),
                    "member_id": record.get("member_id", ""),
                    "persona": record.get("persona", ""),
                    "status": record.get("status", "active"),
                    "content_type": record.get("content_type", ""),
                    "posting_times": record.get("posting_times", ""),
                    "target_audience": record.get("target_audience", "")
                }
                kol_list.append(kol_info)
            else:
                # 兼容舊格式（列表格式）
                if len(record) >= 6:  # 確保有足夠的欄位
                    kol_info = {
                        "serial": record[0] if len(record) > 0 else "",
                        "nickname": record[1] if len(record) > 1 else "",
                        "member_id": record[4] if len(record) > 4 else "",
                        "persona": record[3] if len(record) > 3 else "",
                        "status": record[9] if len(record) > 9 else "",
                        "content_type": record[10] if len(record) > 10 else "",
                        "posting_times": record[11] if len(record) > 11 else "",
                        "target_audience": record[12] if len(record) > 12 else ""
                    }
                    kol_list.append(kol_info)
        
        # 處理貼文數據
        post_list = []
        
        # 檢查數據來源
        if isinstance(post_records, list) and len(post_records) > 0:
            # 從 posting-service 獲取的數據（字典格式）
            if isinstance(post_records[0], dict):
                for record in post_records:
                    post_info = {
                        "post_id": record.get("post_id", ""),
                        "kol_serial": record.get("kol_serial", ""),
                        "kol_nickname": record.get("kol_nickname", ""),
                        "kol_id": record.get("kol_serial", ""),  # 使用 kol_serial 作為 kol_id
                        "persona": record.get("kol_persona", ""),
                        "content_type": "",  # posting-service 沒有這個欄位
                        "topic_id": record.get("topic_id", ""),
                        "topic_title": record.get("topic_title", ""),
                        "content": record.get("content", ""),
                        "status": record.get("status", ""),
                        "post_time": record.get("created_at", ""),
                        "platform_post_id": record.get("cmoney_post_id", ""),
                        "platform_post_url": record.get("cmoney_post_url", ""),
                        "stock_code": record.get("stock_code", ""),
                        "stock_name": record.get("stock_name", ""),
                        "title": record.get("title", ""),
                        "quality_score": record.get("quality_score"),
                        "ai_detection_score": record.get("ai_detection_score"),
                        "risk_level": record.get("risk_level"),
                        "reviewer_notes": record.get("reviewer_notes", ""),
                        "approved_by": record.get("approved_by", ""),
                        "approved_at": record.get("approved_at", ""),
                        "published_at": record.get("published_at", ""),
                        "views": record.get("views", 0),
                        "likes": record.get("likes", 0),
                        "comments": record.get("comments", 0),
                        "shares": record.get("shares", 0),
                        "created_at": record.get("created_at", ""),
                        "updated_at": record.get("updated_at", "")
                    }
                    post_list.append(post_info)
            else:
                # 從 Google Sheets 獲取的數據（列表格式）
                for record in post_records:
                    if len(record) >= 12:  # 確保有足夠的欄位
                        post_info = {
                            "post_id": record[0] if len(record) > 0 else "",
                            "kol_serial": record[1] if len(record) > 1 else "",
                            "kol_nickname": record[2] if len(record) > 2 else "",
                            "kol_id": record[3] if len(record) > 3 else "",
                            "persona": record[4] if len(record) > 4 else "",
                            "content_type": record[5] if len(record) > 5 else "",
                            "topic_id": record[7] if len(record) > 7 else "",
                            "topic_title": record[8] if len(record) > 8 else "",
                            "content": record[10] if len(record) > 10 else "",
                            "status": record[11] if len(record) > 11 else "",
                            "post_time": record[13] if len(record) > 13 else "",
                            "platform_post_id": record[15] if len(record) > 15 else "",
                            "platform_post_url": record[16] if len(record) > 16 else "",
                            # 新增的 KOL 設定欄位
                            "post_type": record[18] if len(record) > 18 else "",  # 發文類型
                            "content_length": record[19] if len(record) > 19 else "",  # 文章長度
                            "kol_weight_settings": record[20] if len(record) > 20 else "",  # KOL權重設定
                            "content_generation_time": record[21] if len(record) > 21 else "",  # 內容生成時間
                            "kol_settings_version": record[22] if len(record) > 22 else ""  # KOL設定版本
                        }
                        post_list.append(post_info)
        
        # 統計數據 - 計算過去一週有發文的活躍 KOL
        from datetime import datetime, timedelta
        one_week_ago = datetime.now() - timedelta(days=7)
        
        # 獲取過去一週有發文的 KOL
        active_kol_ids = set()
        for post in post_list:
            if post["post_time"] and post["status"] == "已發布":
                try:
                    post_time = datetime.strptime(post["post_time"], "%Y-%m-%d %H:%M:%S")
                    if post_time >= one_week_ago:
                        active_kol_ids.add(post["kol_id"])
                except:
                    continue
        
        kol_stats = {
            "total": len(kol_list),
            "active": len(active_kol_ids),  # 過去一週有發文的 KOL 人數
            "by_persona": {}
        }
        
        # 按人設統計
        for kol in kol_list:
            persona = kol["persona"]
            if persona not in kol_stats["by_persona"]:
                kol_stats["by_persona"][persona] = 0
            kol_stats["by_persona"][persona] += 1
        
        post_stats = {
            "total": len(post_list),
            "published": len([p for p in post_list if p["status"] == "已發布"]),
            "pending": len([p for p in post_list if p["status"] == "待發布"]),
            "by_kol": {}
        }
        
        # 按 KOL 統計
        for post in post_list:
            kol_nickname = post["kol_nickname"]
            if kol_nickname not in post_stats["by_kol"]:
                post_stats["by_kol"][kol_nickname] = 0
            post_stats["by_kol"][kol_nickname] += 1
        
        return {
            "timestamp": datetime.now().isoformat(),
            "kol_list": kol_list,
            "post_list": post_list,
            "statistics": {
                "kol_stats": kol_stats,
                "post_stats": post_stats
            }
        }
        
    except Exception as e:
        logger.error(f"獲取內容管理數據失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取內容管理數據失敗: {str(e)}")

@app.delete("/api/dashboard/posts/{post_id}/delete")
async def delete_post(post_id: str):
    """
    刪除貼文 - 使用CMoney API從平台刪除貼文
    """
    try:
        client = get_sheets_client()
        
        # 讀取貼文記錄表
        post_data = client.read_sheet('貼文記錄表', 'A:R')
        if not post_data or len(post_data) < 2:
            raise HTTPException(status_code=404, detail="找不到貼文記錄表")
        
        post_headers = post_data[0]
        post_records = post_data[1:]
        
        # 找到要刪除的貼文
        target_post = None
        for record in post_records:
            if len(record) > 0 and record[0] == post_id:
                target_post = record
                break
        
        if not target_post:
            raise HTTPException(status_code=404, detail=f"找不到貼文 ID: {post_id}")
        
        # 檢查貼文是否已經發布
        if len(target_post) < 16 or not target_post[15]:  # platform_post_id
            raise HTTPException(status_code=400, detail="該貼文尚未發布，無法刪除")
        
        # 檢查貼文是否已經被刪除
        if len(target_post) > 11 and target_post[11] == '已刪除':
            raise HTTPException(status_code=400, detail="該貼文已經被刪除")
        
        # 獲取KOL信息
        kol_serial = target_post[1] if len(target_post) > 1 else ""
        platform_post_id = target_post[15] if len(target_post) > 15 else ""
        
        if not kol_serial:
            raise HTTPException(status_code=400, detail="找不到KOL序號")
        
        # 使用KOL服務登入並刪除貼文
        from kol_service import kol_service
        
        # 登入KOL
        access_token = await kol_service.login_kol(kol_serial)
        if not access_token:
            raise HTTPException(status_code=500, detail=f"KOL {kol_serial} 登入失敗")
        
        # 使用CMoney API刪除貼文
        from src.clients.cmoney.cmoney_client import CMoneyClient
        cmoney_client = CMoneyClient()
        
        delete_success = await cmoney_client.delete_article(access_token, platform_post_id)
        
        if not delete_success:
            raise HTTPException(status_code=500, detail="從CMoney平台刪除貼文失敗")
        
        # 更新貼文狀態為已刪除（僅在我們的記錄中標記）
        post_row_index = None
        for i, record in enumerate(post_records):
            if len(record) > 0 and record[0] == post_id:
                post_row_index = i + 2  # Google Sheets 行號從1開始，加上標題行
                break
        
        if post_row_index:
            update_data = [
                '已刪除',  # 發文狀態 (L欄，索引11)
                '',        # 上次排程時間 (M欄) - 保持不變
                '',        # 發文時間戳記 (N欄) - 清空
                '已刪除 - 管理員從平台刪除',  # 最近錯誤訊息 (O欄)
                platform_post_id,  # 平台發文ID (P欄) - 保持不變
                target_post[16] if len(target_post) > 16 else ''  # 平台發文URL (Q欄) - 保持不變
            ]
            
            # 寫入更新到 Google Sheets
            range_name = f'L{post_row_index}:Q{post_row_index}'
            client.write_sheet('貼文記錄表', [update_data], range_name)
        
        logger.info(f"成功從CMoney平台刪除貼文: {post_id} (平台ID: {platform_post_id})")
        
        return {
            "success": True,
            "message": "貼文已成功從CMoney平台刪除",
            "post_id": post_id,
            "platform_post_id": platform_post_id,
            "kol_serial": kol_serial,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"刪除貼文失敗 {post_id}: {e}")
        raise HTTPException(status_code=500, detail=f"刪除貼文失敗: {str(e)}")

# ==================== 互動分析儀表板 ====================

@app.get("/api/dashboard/interaction-analysis")
async def get_interaction_analysis_data():
    """
    獲取互動分析儀表板數據
    包括 1小時、1日、7日互動數據分析
    """
    try:
        client = get_sheets_client()
        
        # 獲取互動回饋數據
        interaction_tables = ['互動回饋_1hr', '互動回饋_1day', '互動回饋_7days', '互動回饋即時總表']
        interaction_data = {}
        
        for table_name in interaction_tables:
            try:
                data = client.read_sheet(table_name, 'A:O')
                if data and len(data) > 1:
                    headers = data[0]
                    records = data[1:]
                    
                    # 處理互動數據
                    interactions = []
                    for record in records:
                        if len(record) >= 14:  # 確保有足夠的欄位（至少14個）
                            interaction = {
                                "article_id": record[0] if len(record) > 0 else "",
                                "member_id": record[1] if len(record) > 1 else "",
                                "nickname": record[2] if len(record) > 2 else "",
                                "title": record[3] if len(record) > 3 else "",
                                "content": record[4] if len(record) > 4 else "",
                                "topic_id": record[5] if len(record) > 5 else "",
                                "is_trending_topic": record[6] if len(record) > 6 else "",
                                "post_time": record[7] if len(record) > 7 else "",
                                "last_update_time": record[8] if len(record) > 8 else "",
                                "likes_count": int(record[9]) if len(record) > 9 and record[9].isdigit() else 0,
                                "comments_count": int(record[10]) if len(record) > 10 and record[10].isdigit() else 0,
                                "total_interactions": int(record[11]) if len(record) > 11 and record[11].isdigit() else 0,
                                "engagement_rate": float(record[12]) if len(record) > 12 and record[12].replace('.', '').isdigit() else 0.0,
                                "growth_rate": float(record[13]) if len(record) > 13 and record[13].replace('.', '').isdigit() else 0.0,
                                "collection_error": record[14] if len(record) > 14 else "",
                                "donation_count": int(record[15]) if len(record) > 15 and record[15].isdigit() else 0,
                                "donation_amount": float(record[16]) if len(record) > 16 and record[16].replace('.', '').isdigit() else 0.0,
                                "emoji_type": record[17] if len(record) > 17 else "",
                                "emoji_counts": record[18] if len(record) > 18 else "{}",
                                "total_emoji_count": int(record[19]) if len(record) > 19 and record[19].isdigit() else 0
                            }
                            interactions.append(interaction)
                    
                    interaction_data[table_name] = interactions
                else:
                    interaction_data[table_name] = []
            except Exception as e:
                logger.warning(f"讀取 {table_name} 失敗: {e}")
                interaction_data[table_name] = []
        
        # 統計分析
        stats = {}
        for period, data in interaction_data.items():
            if data:
                total_interactions = sum(item["total_interactions"] for item in data)
                total_likes = sum(item["likes_count"] for item in data)
                total_comments = sum(item["comments_count"] for item in data)
                total_donations = sum(item["donation_count"] for item in data)
                total_donation_amount = sum(item["donation_amount"] for item in data)
                total_emoji_count = sum(item["total_emoji_count"] for item in data)
                avg_engagement = sum(item["engagement_rate"] for item in data) / len(data) if data else 0
                
                # 按 KOL 統計
                kol_stats = {}
                for item in data:
                    nickname = item["nickname"]
                    if nickname not in kol_stats:
                                            kol_stats[nickname] = {
                        "total_interactions": 0,
                        "likes": 0,
                        "comments": 0,
                        "posts": 0,
                        "donations": 0,
                        "donation_amount": 0.0,
                        "emoji_count": 0
                    }
                    kol_stats[nickname]["total_interactions"] += item["total_interactions"]
                    kol_stats[nickname]["likes"] += item["likes_count"]
                    kol_stats[nickname]["comments"] += item["comments_count"]
                    kol_stats[nickname]["posts"] += 1
                    kol_stats[nickname]["donations"] += item["donation_count"]
                    kol_stats[nickname]["donation_amount"] += item["donation_amount"]
                    kol_stats[nickname]["emoji_count"] += item["total_emoji_count"]
                
                stats[period] = {
                    "total_posts": len(data),
                    "total_interactions": total_interactions,
                    "total_likes": total_likes,
                    "total_comments": total_comments,
                    "total_donations": total_donations,
                    "total_donation_amount": total_donation_amount,
                    "total_emoji_count": total_emoji_count,
                    "avg_engagement_rate": round(avg_engagement, 3),
                    "kol_performance": kol_stats
                }
            else:
                stats[period] = {
                    "total_posts": 0,
                    "total_interactions": 0,
                    "total_likes": 0,
                    "total_comments": 0,
                    "total_donations": 0,
                    "total_donation_amount": 0.0,
                    "total_emoji_count": 0,
                    "avg_engagement_rate": 0.0,
                    "kol_performance": {}
                }
        
        return {
            "timestamp": datetime.now().isoformat(),
            "interaction_data": interaction_data,
            "statistics": stats,
            "data_source": "google_sheets_real_data"  # 標記為真實數據
        }
        
    except Exception as e:
        logger.error(f"獲取互動分析數據失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取互動分析數據失敗: {str(e)}")

# ==================== KOL角色管理API ====================

from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class KOLUpdateRequest(BaseModel):
    """KOL更新請求"""
    serial: Optional[str] = None
    nickname: Optional[str] = None
    persona: Optional[str] = None
    target_audience: Optional[str] = None
    status: Optional[str] = None
    interaction_threshold: Optional[float] = None
    common_terms: Optional[str] = None
    colloquial_terms: Optional[str] = None
    tone_style: Optional[str] = None
    prompt_persona: Optional[str] = None
    prompt_style: Optional[str] = None
    prompt_guardrails: Optional[str] = None
    prompt_skeleton: Optional[str] = None
    prompt_cta: Optional[str] = None
    prompt_hashtags: Optional[str] = None
    signature: Optional[str] = None
    emoji_pack: Optional[str] = None
    model_id: Optional[str] = None
    model_temp: Optional[float] = None
    max_tokens: Optional[int] = None

class BatchUpdateRequest(BaseModel):
    """批量更新請求"""
    selected_kols: List[str]  # member_id列表
    update_fields: Dict[str, Any]  # 要更新的欄位

@app.put("/api/dashboard/kols/{member_id}")
async def update_kol(
    member_id: str,
    update_request: KOLUpdateRequest
):
    """更新單個KOL設定"""
    try:
        # 欄位映射
        field_mapping = {
            'serial': 0,
            'nickname': 1,
            'owner': 2,
            'persona': 3,
            'member_id': 4,
            'email': 6,
            'password': 7,
            'whitelist': 8,
            'notes': 9,
            'content_types': 10,
            'post_times': 11,
            'target_audience': 12,
            'interaction_threshold': 13,
            'common_terms': 14,
            'colloquial_terms': 15,
            'tone_style': 16,
            'typing_habit': 17,
            'backstory': 18,
            'expertise': 19,
            'data_source': 20,
            'prompt_persona': 21,
            'prompt_style': 22,
            'prompt_guardrails': 23,
            'prompt_skeleton': 24,
            'prompt_cta': 25,
            'prompt_hashtags': 26,
            'signature': 27,
            'emoji_pack': 28,
            'model_id': 29,
            'model_temp': 30,
            'max_tokens': 31
        }
        
        # 獲取當前數據
        data = sheets_client.read_sheet('同學會帳號管理', 'A:AZ')
        if len(data) < 2:
            raise HTTPException(status_code=404, detail="KOL數據不存在")
        
        headers = data[0]
        updated = False
        
        # 找到對應的行並更新
        for i, row in enumerate(data[1:], start=2):  # 從第2行開始
            if len(row) > 4 and row[4] == member_id:
                # 更新欄位
                for field, value in update_request.dict(exclude_unset=True).items():
                    if field in field_mapping:
                        col_index = field_mapping[field]
                        # 確保行有足夠的列
                        while len(row) <= col_index:
                            row.append('')
                        row[col_index] = str(value) if value is not None else ''
                
                # 寫回Google Sheets
                range_name = f'同學會帳號管理!A{i}:AZ{i}'
                sheets_client.write_sheet('同學會帳號管理', [row], range_name)
                updated = True
                break
        
        if updated:
            return {
                "success": True,
                "message": "KOL設定已更新",
                "member_id": member_id,
                "updated_at": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=404, detail="KOL不存在")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新KOL失敗: {e}")
        raise HTTPException(status_code=500, detail=f"更新失敗: {str(e)}")

@app.post("/api/dashboard/kols/batch-update")
async def batch_update_kols(
    request: BatchUpdateRequest,
):
    """批量更新KOL設定"""
    try:
        success_count = 0
        failed_count = 0
        errors = []
        
        # 欄位映射
        field_mapping = {
            'serial': 0, 'nickname': 1, 'owner': 2, 'persona': 3, 'member_id': 4,
            'email': 6, 'password': 7, 'whitelist': 8, 'notes': 9, 'content_types': 10,
            'post_times': 11, 'target_audience': 12, 'interaction_threshold': 13,
            'common_terms': 14, 'colloquial_terms': 15, 'tone_style': 16,
            'typing_habit': 17, 'backstory': 18, 'expertise': 19, 'data_source': 20,
            'prompt_persona': 21, 'prompt_style': 22, 'prompt_guardrails': 23,
            'prompt_skeleton': 24, 'prompt_cta': 25, 'prompt_hashtags': 26,
            'signature': 27, 'emoji_pack': 28, 'model_id': 29, 'model_temp': 30,
            'max_tokens': 31
        }
        
        # 獲取當前數據
        data = sheets_client.read_sheet('同學會帳號管理', 'A:AZ')
        if len(data) < 2:
            raise HTTPException(status_code=404, detail="KOL數據不存在")
        
        headers = data[0]
        
        for member_id in request.selected_kols:
            try:
                # 找到對應的行並更新
                for i, row in enumerate(data[1:], start=2):
                    if len(row) > 4 and row[4] == member_id:
                        # 更新欄位
                        for field, value in request.update_fields.items():
                            if field in field_mapping:
                                col_index = field_mapping[field]
                                while len(row) <= col_index:
                                    row.append('')
                                row[col_index] = str(value) if value is not None else ''
                        
                        # 寫回Google Sheets
                        range_name = f'同學會帳號管理!A{i}:AZ{i}'
                        sheets_client.write_sheet('同學會帳號管理', [row], range_name)
                        success_count += 1
                        break
                else:
                    failed_count += 1
                    errors.append(f"KOL {member_id} 不存在")
                    
            except Exception as e:
                failed_count += 1
                error_msg = f"KOL {member_id} 更新異常: {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg)
        
        return {
            "success": failed_count == 0,
            "message": f"批量更新完成: 成功 {success_count} 個，失敗 {failed_count} 個",
            "updated_count": success_count,
            "failed_count": failed_count,
            "errors": errors
        }
        
    except Exception as e:
        logger.error(f"批量更新失敗: {e}")
        raise HTTPException(status_code=500, detail=f"批量更新失敗: {str(e)}")

@app.get("/api/dashboard/kols/{member_id}/settings")
async def get_kol_settings(
    member_id: str,
):
    """獲取KOL完整設定"""
    try:
        # 獲取KOL基本資訊
        kol_data = sheets_client.read_sheet('同學會帳號管理', 'A:AZ')
        kol_records = kol_data[1:] if len(kol_data) > 1 else []
        
        # 查找特定KOL
        kol_info = None
        for record in kol_records:
            if len(record) > 4 and record[4] == member_id:
                kol_info = {
                    "serial": record[0] if len(record) > 0 else "",
                    "nickname": record[1] if len(record) > 1 else "",
                    "member_id": record[4] if len(record) > 4 else "",
                    "persona": record[3] if len(record) > 3 else "",
                    "status": record[9] if len(record) > 9 else "",
                    "owner": record[2] if len(record) > 2 else "",
                    "email": record[6] if len(record) > 6 else "",
                    "password": record[7] if len(record) > 7 else "",
                    "whitelist": record[8] == "TRUE" if len(record) > 8 else False,
                    "notes": record[9] if len(record) > 9 else "",
                    "post_times": record[11] if len(record) > 11 else "",
                    "target_audience": record[12] if len(record) > 12 else "",
                    "interaction_threshold": float(record[13]) if len(record) > 13 and record[13].replace('.', '').isdigit() else 0.0,
                    "content_types": record[10].split(',') if len(record) > 10 and record[10] else [],
                    "common_terms": record[14] if len(record) > 14 else "",
                    "colloquial_terms": record[15] if len(record) > 15 else "",
                    "tone_style": record[16] if len(record) > 16 else "",
                    "typing_habit": record[17] if len(record) > 17 else "",
                    "backstory": record[18] if len(record) > 18 else "",
                    "expertise": record[19] if len(record) > 19 else "",
                    "data_source": record[20] if len(record) > 20 else "",
                    "prompt_persona": record[21] if len(record) > 21 else "",
                    "prompt_style": record[22] if len(record) > 22 else "",
                    "prompt_guardrails": record[23] if len(record) > 23 else "",
                    "prompt_skeleton": record[24] if len(record) > 24 else "",
                    "prompt_cta": record[25] if len(record) > 25 else "",
                    "prompt_hashtags": record[26] if len(record) > 26 else "",
                    "signature": record[27] if len(record) > 27 else "",
                    "emoji_pack": record[28] if len(record) > 28 else "",
                    "model_id": record[29] if len(record) > 29 else "",
                    "model_temp": float(record[30]) if len(record) > 30 and record[30].replace('.', '').isdigit() else 0.0,
                    "max_tokens": int(record[31]) if len(record) > 31 and record[31].isdigit() else 0,
                    "created_time": datetime.now().isoformat(),
                    "last_updated": datetime.now().isoformat()
                }
                break
        
        if kol_info:
            return {
                "success": True,
                "data": kol_info,
                "member_id": member_id
            }
        else:
            raise HTTPException(status_code=404, detail="KOL不存在")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"獲取KOL設定失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取設定失敗: {str(e)}")

# ==================== KOL 詳情 API ====================

@app.get("/api/dashboard/kols/{member_id}")
async def get_kol_detail(member_id: str):
    """
    獲取 KOL 個人詳情
    包括基本資訊、發文統計、設定等
    """
    try:
        client = get_sheets_client()
        
        # 獲取 KOL 基本資訊
        kol_data = client.read_sheet('同學會帳號管理', 'A:AZ')
        kol_records = kol_data[1:] if len(kol_data) > 1 else []
        
        # 查找特定 KOL
        kol_info = None
        for record in kol_records:
            if len(record) > 4 and record[4] == member_id:
                kol_info = {
                    "serial": record[0] if len(record) > 0 else "",
                    "nickname": record[1] if len(record) > 1 else "",
                    "member_id": record[4] if len(record) > 4 else "",
                    "persona": record[3] if len(record) > 3 else "",
                    "status": record[9] if len(record) > 9 else "",
                    "owner": record[2] if len(record) > 2 else "",
                    "email": record[6] if len(record) > 6 else "",
                    "password": record[7] if len(record) > 7 else "",
                    "whitelist": record[8] == "TRUE" if len(record) > 8 else False,
                    "notes": record[9] if len(record) > 9 else "",
                    "post_times": record[11] if len(record) > 11 else "",
                    "target_audience": record[12] if len(record) > 12 else "",
                    "interaction_threshold": float(record[13]) if len(record) > 13 and record[13].replace('.', '').isdigit() else 0.0,
                    "content_types": record[10].split(',') if len(record) > 10 and record[10] else [],
                    "common_terms": record[14] if len(record) > 14 else "",
                    "colloquial_terms": record[15] if len(record) > 15 else "",
                    "tone_style": record[16] if len(record) > 16 else "",
                    "typing_habit": record[17] if len(record) > 17 else "",
                    "backstory": record[18] if len(record) > 18 else "",
                    "expertise": record[19] if len(record) > 19 else "",
                    "data_source": record[20] if len(record) > 20 else "",
                    "created_time": record[21] if len(record) > 21 else "",
                    "last_updated": record[22] if len(record) > 22 else "",
                    "prompt_persona": record[23] if len(record) > 23 else "",
                    "prompt_style": record[24] if len(record) > 24 else "",
                    "prompt_guardrails": record[25] if len(record) > 25 else "",
                    "prompt_skeleton": record[26] if len(record) > 26 else "",
                    "prompt_cta": record[27] if len(record) > 27 else "",
                    "prompt_hashtags": record[28] if len(record) > 28 else "",
                    "signature": record[29] if len(record) > 29 else "",
                    "emoji_pack": record[30] if len(record) > 30 else "",
                    "model_id": record[31] if len(record) > 31 else "",
                    "model_temp": float(record[32]) if len(record) > 32 and record[32].replace('.', '').isdigit() else 0.0,
                    "max_tokens": int(record[33]) if len(record) > 33 and record[33].isdigit() else 0
                }
                break
        
        if not kol_info:
            raise HTTPException(status_code=404, detail=f"找不到 Member ID: {member_id}")
        
        # 獲取發文統計
        post_data = client.read_sheet('貼文記錄表', 'A:R')
        post_records = post_data[1:] if len(post_data) > 1 else []
        
        # 篩選該 KOL 的貼文
        kol_posts = [row for row in post_records if len(row) > 3 and row[3] == member_id]
        
        # 計算統計數據
        total_posts = len(kol_posts)
        published_posts = len([p for p in kol_posts if len(p) > 11 and p[11] == "已發布"])
        draft_posts = len([p for p in kol_posts if len(p) > 11 and p[11] == "草稿"])
        
        # 獲取互動數據統計
        interaction_stats = await get_kol_interaction_stats(member_id, client)
        
        # 獲取歷史趨勢數據
        trend_data = await get_kol_interaction_trend(member_id, client, "7days")
        
        statistics = {
            "total_posts": total_posts,
            "published_posts": published_posts,
            "draft_posts": draft_posts,
            "avg_interaction_rate": interaction_stats.get("avg_interaction_rate", 0.0),
            "best_performing_post": interaction_stats.get("best_performing_post", ""),
            "total_interactions": interaction_stats.get("total_interactions", 0),
            "avg_likes_per_post": interaction_stats.get("avg_likes_per_post", 0),
            "avg_comments_per_post": interaction_stats.get("avg_comments_per_post", 0),
            # 新增歷史趨勢數據
            "trend_data": trend_data,
            "monthly_stats": await get_kol_monthly_stats(member_id, client),
            "weekly_stats": await get_kol_weekly_stats(member_id, client),
            "daily_stats": await get_kol_daily_stats(member_id, client)
        }
        
        return {
            "timestamp": datetime.now().isoformat(),
            "success": True,
            "data": {
                "kol_info": kol_info,
                "statistics": statistics
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"獲取 KOL 詳情失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取 KOL 詳情失敗: {str(e)}")

@app.get("/api/dashboard/kols/{member_id}/posts")
async def get_kol_posts(member_id: str, page: int = 1, page_size: int = 10, status: str = "all"):
    """
    獲取 KOL 的發文歷史
    支持分頁和狀態篩選
    """
    try:
        client = get_sheets_client()
        
        # 獲取貼文數據
        post_data = client.read_sheet('貼文記錄表', 'A:R')
        post_records = post_data[1:] if len(post_data) > 1 else []
        
        # 篩選該 KOL 的貼文
        kol_posts = []
        for row in post_records:
            if len(row) > 3 and row[3] == member_id:
                # 狀態篩選
                if status != "all" and len(row) > 11 and row[11] != status:
                    continue
                
                post_record = {
                    "post_id": row[0] if len(row) > 0 else "",
                    "kol_serial": row[1] if len(row) > 1 else "",
                    "kol_nickname": row[2] if len(row) > 2 else "",
                    "kol_member_id": row[3] if len(row) > 3 else "",
                    "persona": row[4] if len(row) > 4 else "",
                    "content_type": row[5] if len(row) > 5 else "",
                    "topic_index": int(row[6]) if len(row) > 6 and row[6].isdigit() else 0,
                    "topic_id": row[7] if len(row) > 7 else "",
                    "topic_title": row[8] if len(row) > 8 else "",
                    "topic_keywords": row[9] if len(row) > 9 else "",
                    "content": row[10] if len(row) > 10 else "",
                    "status": row[11] if len(row) > 11 else "",
                    "scheduled_time": row[12] if len(row) > 12 else "",
                    "post_time": row[13] if len(row) > 13 else "",
                    "error_message": row[14] if len(row) > 14 else "",
                    "platform_post_id": row[15] if len(row) > 15 else "",
                    "platform_post_url": row[16] if len(row) > 16 else "",
                    "trending_topic_title": row[17] if len(row) > 17 else ""
                }
                kol_posts.append(post_record)
        
        # 分頁處理
        total_items = len(kol_posts)
        total_pages = (total_items + page_size - 1) // page_size
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        paginated_posts = kol_posts[start_index:end_index]
        
        # 獲取互動數據
        for post in paginated_posts:
            interactions = await get_post_interactions(post["post_id"], client)
            post["interactions"] = interactions
        
        return {
            "timestamp": datetime.now().isoformat(),
            "success": True,
            "data": {
                "posts": paginated_posts,
                "pagination": {
                    "current_page": page,
                    "page_size": page_size,
                    "total_pages": total_pages,
                    "total_items": total_items
                }
            }
        }
        
    except Exception as e:
        logger.error(f"獲取 KOL 發文歷史失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取 KOL 發文歷史失敗: {str(e)}")

@app.get("/api/dashboard/kols/{member_id}/interactions")
async def get_kol_interactions(member_id: str, timeframe: str = "7days", start_date: str = None, end_date: str = None):
    """
    獲取 KOL 的互動數據分析
    """
    try:
        client = get_sheets_client()
        
        # 獲取互動數據
        interaction_stats = await get_kol_interaction_stats(member_id, client)
        
        # 獲取互動趨勢數據
        trend_data = await get_kol_interaction_trend(member_id, client, timeframe)
        
        # 獲取按話題的表現數據
        topic_performance = await get_kol_topic_performance(member_id, client)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "success": True,
            "data": {
                "interaction_summary": interaction_stats,
                "interaction_trend": trend_data,
                "performance_by_topic": topic_performance
            }
        }
        
    except Exception as e:
        logger.error(f"獲取 KOL 互動數據失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取 KOL 互動數據失敗: {str(e)}")

# ==================== 輔助函數 ====================

async def get_kol_interaction_stats(member_id: str):
    """獲取 KOL 互動統計數據"""
    try:
        # 讀取 7 天互動數據
        interaction_data = client.read_sheet('互動回饋_7days', 'A:O')
        if not interaction_data or len(interaction_data) <= 1:
            return {
                "total_posts": 0,
                "avg_interaction_rate": 0.0,
                "best_performing_post": "",
                "total_interactions": 0,
                "avg_likes_per_post": 0,
                "avg_comments_per_post": 0
            }
        
        # 篩選該 KOL 的互動數據
        kol_interactions = []
        for row in interaction_data[1:]:  # 跳過標題行
            if len(row) > 1 and row[1] == member_id:
                interaction = {
                    "article_id": row[0] if len(row) > 0 else "",
                    "likes_count": int(row[9]) if len(row) > 9 and row[9].isdigit() else 0,
                    "comments_count": int(row[10]) if len(row) > 10 and row[10].isdigit() else 0,
                    "total_interactions": int(row[11]) if len(row) > 11 and row[11].isdigit() else 0,
                    "engagement_rate": float(row[12]) if len(row) > 12 and row[12].replace('.', '').isdigit() else 0.0
                }
                kol_interactions.append(interaction)
        
        if not kol_interactions:
            return {
                "total_posts": 0,
                "avg_interaction_rate": 0.0,
                "best_performing_post": "",
                "total_interactions": 0,
                "avg_likes_per_post": 0,
                "avg_comments_per_post": 0
            }
        
        # 計算統計數據
        total_posts = len(kol_interactions)
        total_interactions = sum(i["total_interactions"] for i in kol_interactions)
        total_likes = sum(i["likes_count"] for i in kol_interactions)
        total_comments = sum(i["comments_count"] for i in kol_interactions)
        avg_interaction_rate = sum(i["engagement_rate"] for i in kol_interactions) / total_posts if total_posts > 0 else 0.0
        
        # 找到最佳表現貼文
        best_post = max(kol_interactions, key=lambda x: x["total_interactions"]) if kol_interactions else None
        best_performing_post = best_post["article_id"] if best_post else ""
        
        return {
            "total_posts": total_posts,
            "avg_interaction_rate": round(avg_interaction_rate, 3),
            "best_performing_post": best_performing_post,
            "total_interactions": total_interactions,
            "avg_likes_per_post": round(total_likes / total_posts, 1) if total_posts > 0 else 0,
            "avg_comments_per_post": round(total_comments / total_posts, 1) if total_posts > 0 else 0
        }
        
    except Exception as e:
        logger.error(f"獲取 KOL 互動統計失敗: {e}")
        return {
            "total_posts": 0,
            "avg_interaction_rate": 0.0,
            "best_performing_post": "",
            "total_interactions": 0,
            "avg_likes_per_post": 0,
            "avg_comments_per_post": 0
        }

async def get_post_interactions(post_id: str):
    """獲取特定貼文的互動數據"""
    interactions = {
        "1hr": {"likes_count": 0, "comments_count": 0, "total_interactions": 0, "engagement_rate": 0.0, "growth_rate": 0.0},
        "1day": {"likes_count": 0, "comments_count": 0, "total_interactions": 0, "engagement_rate": 0.0, "growth_rate": 0.0},
        "7days": {"likes_count": 0, "comments_count": 0, "total_interactions": 0, "engagement_rate": 0.0, "growth_rate": 0.0}
    }
    
    timeframes = ["1hr", "1day", "7days"]
    sheet_names = ["互動回饋_1hr", "互動回饋_1day", "互動回饋_7days"]
    
    for timeframe, sheet_name in zip(timeframes, sheet_names):
        try:
            data = client.read_sheet(sheet_name, 'A:O')
            if data and len(data) > 1:
                for row in data[1:]:  # 跳過標題行
                    if len(row) > 0 and row[0] == post_id:
                        interactions[timeframe] = {
                            "likes_count": int(row[9]) if len(row) > 9 and row[9].isdigit() else 0,
                            "comments_count": int(row[10]) if len(row) > 10 and row[10].isdigit() else 0,
                            "total_interactions": int(row[11]) if len(row) > 11 and row[11].isdigit() else 0,
                            "engagement_rate": float(row[12]) if len(row) > 12 and row[12].replace('.', '').isdigit() else 0.0,
                            "growth_rate": float(row[13]) if len(row) > 13 and row[13].replace('.', '').isdigit() else 0.0
                        }
                        break
        except Exception as e:
            logger.warning(f"讀取 {sheet_name} 失敗: {e}")
            continue
    
    return interactions

async def get_kol_interaction_trend(member_id: str, timeframe: str = "7days"):
    """獲取 KOL 互動趨勢數據"""
    # 這裡可以實現更複雜的趨勢分析
    # 暫時返回簡單的模擬數據
    return [
        {
            "date": "2024-01-01",
            "posts_count": 2,
            "total_interactions": 150,
            "avg_engagement_rate": 0.05,
            "likes": 120,
            "comments": 30
        },
        {
            "date": "2024-01-02",
            "posts_count": 1,
            "total_interactions": 85,
            "avg_engagement_rate": 0.042,
            "likes": 70,
            "comments": 15
        }
    ]

async def get_kol_topic_performance(member_id: str):
    """獲取 KOL 按話題的表現數據"""
    # 這裡可以實現按話題的表現分析
    # 暫時返回簡單的模擬數據
    return [
        {
            "topic_id": "topic-001",
            "topic_title": "技術分析",
            "posts_count": 8,
            "avg_interaction_rate": 0.052,
            "total_interactions": 420
        },
        {
            "topic_id": "topic-002",
            "topic_title": "圖表解讀",
            "posts_count": 6,
            "avg_interaction_rate": 0.048,
            "total_interactions": 290
        }
    ]

async def get_kol_monthly_stats(member_id: str):
    """獲取 KOL 月度統計數據"""
    try:
        # 讀取貼文記錄表，按月份統計
        post_data = client.read_sheet('貼文記錄表', 'A:R')
        post_records = post_data[1:] if len(post_data) > 1 else []
        
        # 篩選該 KOL 的貼文
        kol_posts = [row for row in post_records if len(row) > 3 and row[3] == member_id]
        
        # 按月份分組統計
        monthly_stats = {}
        for post in kol_posts:
            if len(post) > 13 and post[13]:  # post_time
                try:
                    post_time = datetime.strptime(post[13], "%Y-%m-%d %H:%M:%S")
                    month_key = post_time.strftime("%Y-%m")
                    
                    if month_key not in monthly_stats:
                        monthly_stats[month_key] = {
                            "posts_count": 0,
                            "total_interactions": 0,
                            "avg_likes_per_post": 0,
                            "avg_comments_per_post": 0,
                            "engagement_rate": 0.0
                        }
                    
                    monthly_stats[month_key]["posts_count"] += 1
                    
                    # 這裡可以添加互動數據的統計
                    # 暫時使用模擬數據
                    monthly_stats[month_key]["total_interactions"] += 50 + (monthly_stats[month_key]["posts_count"] * 10)
                    monthly_stats[month_key]["avg_likes_per_post"] = round(monthly_stats[month_key]["total_interactions"] * 0.8 / monthly_stats[month_key]["posts_count"], 1)
                    monthly_stats[month_key]["avg_comments_per_post"] = round(monthly_stats[month_key]["total_interactions"] * 0.2 / monthly_stats[month_key]["posts_count"], 1)
                    monthly_stats[month_key]["engagement_rate"] = round(monthly_stats[month_key]["total_interactions"] / (monthly_stats[month_key]["posts_count"] * 1000), 3)
                    
                except:
                    continue
        
        # 轉換為列表格式，按月份排序
        result = []
        for month, stats in sorted(monthly_stats.items()):
            result.append({
                "month": month,
                **stats
            })
        
        return result
        
    except Exception as e:
        logger.error(f"獲取 KOL 月度統計失敗: {e}")
        return []

async def get_kol_weekly_stats(member_id: str):
    """獲取 KOL 週度統計數據"""
    try:
        # 讀取貼文記錄表，按週統計
        post_data = client.read_sheet('貼文記錄表', 'A:R')
        post_records = post_data[1:] if len(post_data) > 1 else []
        
        # 篩選該 KOL 的貼文
        kol_posts = [row for row in post_records if len(row) > 3 and row[3] == member_id]
        
        # 按週分組統計
        weekly_stats = {}
        for post in kol_posts:
            if len(post) > 13 and post[13]:  # post_time
                try:
                    post_time = datetime.strptime(post[13], "%Y-%m-%d %H:%M:%S")
                    # 獲取週數
                    week_number = post_time.isocalendar()[1]
                    year = post_time.year
                    week_key = f"{year}-W{week_number:02d}"
                    
                    if week_key not in weekly_stats:
                        weekly_stats[week_key] = {
                            "week": week_key,
                            "posts_count": 0,
                            "total_interactions": 0,
                            "avg_likes_per_post": 0,
                            "avg_comments_per_post": 0,
                            "engagement_rate": 0.0
                        }
                    
                    weekly_stats[week_key]["posts_count"] += 1
                    
                    # 模擬互動數據
                    weekly_stats[week_key]["total_interactions"] += 30 + (weekly_stats[week_key]["posts_count"] * 8)
                    weekly_stats[week_key]["avg_likes_per_post"] = round(weekly_stats[week_key]["total_interactions"] * 0.8 / weekly_stats[week_key]["posts_count"], 1)
                    weekly_stats[week_key]["avg_comments_per_post"] = round(weekly_stats[week_key]["total_interactions"] * 0.2 / weekly_stats[week_key]["posts_count"], 1)
                    weekly_stats[week_key]["engagement_rate"] = round(weekly_stats[week_key]["total_interactions"] / (weekly_stats[week_key]["posts_count"] * 1000), 3)
                    
                except:
                    continue
        
        # 轉換為列表格式，按週排序
        result = []
        for week, stats in sorted(weekly_stats.items()):
            result.append(stats)
        
        return result
        
    except Exception as e:
        logger.error(f"獲取 KOL 週度統計失敗: {e}")
        return []

async def get_kol_daily_stats(member_id: str):
    """獲取 KOL 日度統計數據"""
    try:
        # 讀取貼文記錄表，按日統計
        post_data = client.read_sheet('貼文記錄表', 'A:R')
        post_records = post_data[1:] if len(post_data) > 1 else []
        
        # 篩選該 KOL 的貼文
        kol_posts = [row for row in post_records if len(row) > 3 and row[3] == member_id]
        
        # 按日分組統計
        daily_stats = {}
        for post in kol_posts:
            if len(post) > 13 and post[13]:  # post_time
                try:
                    post_time = datetime.strptime(post[13], "%Y-%m-%d %H:%M:%S")
                    day_key = post_time.strftime("%Y-%m-%d")
                    
                    if day_key not in daily_stats:
                        daily_stats[day_key] = {
                            "date": day_key,
                            "posts_count": 0,
                            "total_interactions": 0,
                            "avg_likes_per_post": 0,
                            "avg_comments_per_post": 0,
                            "engagement_rate": 0.0
                        }
                    
                    daily_stats[day_key]["posts_count"] += 1
                    
                    # 模擬互動數據
                    daily_stats[day_key]["total_interactions"] += 20 + (daily_stats[day_key]["posts_count"] * 5)
                    daily_stats[day_key]["avg_likes_per_post"] = round(daily_stats[day_key]["total_interactions"] * 0.8 / daily_stats[day_key]["posts_count"], 1)
                    daily_stats[day_key]["avg_comments_per_post"] = round(daily_stats[day_key]["total_interactions"] * 0.2 / daily_stats[day_key]["posts_count"], 1)
                    daily_stats[day_key]["engagement_rate"] = round(daily_stats[day_key]["total_interactions"] / (daily_stats[day_key]["posts_count"] * 1000), 3)
                    
                except:
                    continue
        
        # 轉換為列表格式，按日期排序
        result = []
        for day, stats in sorted(daily_stats.items()):
            result.append(stats)
        
        return result
        
    except Exception as e:
        logger.error(f"獲取 KOL 日度統計失敗: {e}")
        return []

@app.get("/api/dashboard/article/{article_id}")
async def get_article_details(article_id: str):
    """獲取特定文章的詳細信息"""
    try:
        client = get_sheets_client()
        
        # 獲取貼文數據
        post_data = client.read_sheet('貼文記錄表', 'A:R')
        post_records = post_data[1:] if len(post_data) > 1 else []
        
        # 查找特定文章
        for record in post_records:
            if len(record) > 0 and record[0] == article_id:
                return {
                    "article_id": article_id,
                    "kol_serial": record[1] if len(record) > 1 else "",
                    "kol_nickname": record[2] if len(record) > 2 else "",
                    "kol_id": record[3] if len(record) > 3 else "",
                    "persona": record[4] if len(record) > 4 else "",
                    "content_type": record[5] if len(record) > 5 else "",
                    "topic_id": record[7] if len(record) > 7 else "",
                    "topic_title": record[8] if len(record) > 8 else "",
                    "content": record[10] if len(record) > 10 else "",
                    "status": record[11] if len(record) > 11 else "",
                    "post_time": record[13] if len(record) > 13 else "",
                    "platform_post_id": record[15] if len(record) > 15 else "",
                    "platform_post_url": record[16] if len(record) > 16 else ""
                }
        
        raise HTTPException(status_code=404, detail=f"找不到 Article ID: {article_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"獲取文章詳細信息失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取文章詳細信息失敗: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8007)
