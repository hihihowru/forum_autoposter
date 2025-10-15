"""
互動數據刷新服務
提供API端點來刷新所有歷史Article ID的互動數據
"""

import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

# 添加專案根目錄到 Python 路徑
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

# from src.clients.cmoney.cmoney_client import CMoneyClient, LoginCredentials  # 暫時註解
# from src.clients.google.sheets_client import GoogleSheetsClient  # Google Sheets 已棄用

logger = logging.getLogger(__name__)

# 創建路由器
router = APIRouter(prefix="/api/interaction", tags=["interaction"])

class RefreshRequest(BaseModel):
    """刷新請求模型"""
    force_refresh: bool = False  # 是否強制刷新所有數據
    article_ids: Optional[List[str]] = None  # 指定要刷新的Article ID列表

class RefreshResponse(BaseModel):
    """刷新響應模型"""
    success: bool
    message: str
    task_id: Optional[str] = None
    total_articles: int = 0
    processed_articles: int = 0
    failed_articles: int = 0
    start_time: str
    estimated_completion: Optional[str] = None

class InteractionRefreshService:
    """互動數據刷新服務"""
    
    def __init__(self):
        # self.cmoney_client = CMoneyClient()  # 暫時註解
        # self.sheets_client = GoogleSheetsClient(...)  # Google Sheets 已棄用
        self.cmoney_client = None
        self.sheets_client = None
        self.refresh_tasks = {}  # 存儲刷新任務狀態
    
    async def get_all_article_ids(self) -> List[str]:
        """從Google Sheets獲取所有歷史Article ID"""
        try:
            # 從貼文記錄表獲取所有Article ID
            post_data = self.sheets_client.read_sheet('貼文記錄表', 'A:Z')
            
            if not post_data or len(post_data) < 2:
                logger.warning("沒有找到貼文記錄數據")
                return []
            
            headers = post_data[0]
            rows = post_data[1:]
            
            # 找到platform_post_id欄位索引
            platform_post_id_idx = None
            for i, header in enumerate(headers):
                if 'platform_post_id' in header.lower() or '貼文id' in header.lower():
                    platform_post_id_idx = i
                    break
            
            if platform_post_id_idx is None:
                logger.error("找不到platform_post_id欄位")
                return []
            
            # 提取所有Article ID
            article_ids = []
            for row in rows:
                if len(row) > platform_post_id_idx and row[platform_post_id_idx]:
                    article_id = row[platform_post_id_idx].strip()
                    if article_id and article_id not in article_ids:
                        article_ids.append(article_id)
            
            logger.info(f"找到 {len(article_ids)} 個Article ID")
            return article_ids
            
        except Exception as e:
            logger.error(f"獲取Article ID失敗: {e}")
            return []
    
    async def refresh_article_interaction(self, article_id: str, kol_credentials: Any) -> Dict[str, Any]:
        """刷新單個Article的互動數據"""
        try:
            # 登入獲取token
            login_result = await self.cmoney_client.login(kol_credentials)
            if not login_result or login_result.is_expired:
                return {
                    "success": False,
                    "error": "登入失敗",
                    "article_id": article_id
                }
            
            # 獲取互動數據
            interaction_data = await self.cmoney_client.get_article_interactions(
                login_result.token, 
                article_id
            )
            
            if interaction_data:
                return {
                    "success": True,
                    "article_id": article_id,
                    "data": {
                        "likes": interaction_data.likes,
                        "comments": interaction_data.comments,
                        "shares": interaction_data.shares,
                        "views": interaction_data.views,
                        "engagement_rate": interaction_data.engagement_rate,
                        "emoji_count": interaction_data.raw_data.get('emojiCount', {}) if interaction_data.raw_data else {},
                        "comment_count": interaction_data.raw_data.get('commentCount', 0) if interaction_data.raw_data else 0,
                        "interested_count": interaction_data.raw_data.get('interestedCount', 0) if interaction_data.raw_data else 0,
                        "collected_count": interaction_data.raw_data.get('collectedCount', 0) if interaction_data.raw_data else 0
                    }
                }
            else:
                return {
                    "success": False,
                    "error": "無法獲取互動數據",
                    "article_id": article_id
                }
                
        except Exception as e:
            logger.error(f"刷新Article {article_id} 失敗: {e}")
            return {
                "success": False,
                "error": str(e),
                "article_id": article_id
            }
    
    async def update_interaction_sheets(self, interaction_results: List[Dict[str, Any]]):
        """更新Google Sheets中的互動數據"""
        try:
            # 準備要寫入的數據
            update_data = []
            
            for result in interaction_results:
                if result["success"]:
                    data = result["data"]
                    # 計算總互動數
                    total_interactions = data["likes"] + data["comments"] + data["shares"]
                    
                    # 準備行數據
                    row_data = [
                        result["article_id"],  # Article ID
                        "",  # Member ID (需要從其他地方獲取)
                        "",  # 暱稱 (需要從其他地方獲取)
                        "",  # 標題 (需要從其他地方獲取)
                        "",  # 內容 (需要從其他地方獲取)
                        "",  # Topic ID (需要從其他地方獲取)
                        "",  # 是否為熱門話題
                        datetime.now().isoformat(),  # 發文時間
                        datetime.now().isoformat(),  # 最後更新時間
                        data["likes"],  # 讚數
                        data["comments"],  # 留言數
                        total_interactions,  # 總互動數
                        data["engagement_rate"],  # 互動率
                        0.0,  # 成長率 (需要計算)
                        ""  # 收集錯誤
                    ]
                    update_data.append(row_data)
            
            if update_data:
                # 更新到各個時間週期的表格
                tables = ['互動回饋_1hr', '互動回饋_1day', '互動回饋_7days']
                
                for table_name in tables:
                    try:
                        # 讀取現有數據
                        existing_data = self.sheets_client.read_sheet(table_name, 'A:O')
                        
                        if existing_data:
                            # 更新現有數據
                            for row_data in update_data:
                                article_id = row_data[0]
                                
                                # 查找是否已存在
                                found = False
                                for i, existing_row in enumerate(existing_data[1:], 1):  # 跳過標題行
                                    if len(existing_row) > 0 and existing_row[0] == article_id:
                                        # 更新現有行
                                        existing_data[i] = row_data
                                        found = True
                                        break
                                
                                if not found:
                                    # 添加新行
                                    existing_data.append(row_data)
                            
                            # 寫回Google Sheets
                            self.sheets_client.write_sheet(table_name, existing_data, 'A:O')
                            logger.info(f"更新 {table_name} 成功，共 {len(update_data)} 條記錄")
                        else:
                            # 創建新表格
                            headers = [
                                'Article ID', 'Member ID', '暱稱', '標題', '生成內文', 'Topic ID',
                                '是否為熱門話題', '發文時間', '最後更新時間', '讚數', '留言數',
                                '總互動數', '互動率', '成長率', '收集錯誤'
                            ]
                            new_data = [headers] + update_data
                            self.sheets_client.write_sheet(table_name, new_data, 'A:O')
                            logger.info(f"創建 {table_name} 成功，共 {len(update_data)} 條記錄")
                            
                    except Exception as e:
                        logger.error(f"更新 {table_name} 失敗: {e}")
            
        except Exception as e:
            logger.error(f"更新Google Sheets失敗: {e}")
            raise
    
    async def refresh_all_interactions(self, force_refresh: bool = False, article_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """刷新所有互動數據"""
        start_time = datetime.now()
        task_id = f"refresh_{start_time.strftime('%Y%m%d_%H%M%S')}"
        
        try:
            # 獲取要刷新的Article ID列表
            if article_ids:
                target_article_ids = article_ids
            else:
                target_article_ids = await self.get_all_article_ids()
            
            if not target_article_ids:
                return {
                    "success": False,
                    "message": "沒有找到要刷新的Article ID",
                    "task_id": task_id,
                    "total_articles": 0,
                    "processed_articles": 0,
                    "failed_articles": 0,
                    "start_time": start_time.isoformat()
                }
            
            # 使用川川哥的憑證 (實際應該根據Article ID對應的KOL選擇憑證)
            kol_credentials = LoginCredentials(
                email='forum_200@cmoney.com.tw',
                password='N9t1kY3x'
            )
            
            # 批量刷新互動數據
            interaction_results = []
            processed_count = 0
            failed_count = 0
            
            logger.info(f"開始刷新 {len(target_article_ids)} 個Article的互動數據")
            
            for i, article_id in enumerate(target_article_ids):
                try:
                    result = await self.refresh_article_interaction(article_id, kol_credentials)
                    interaction_results.append(result)
                    
                    if result["success"]:
                        processed_count += 1
                    else:
                        failed_count += 1
                    
                    # 每處理10個Article就更新一次Google Sheets
                    if (i + 1) % 10 == 0:
                        await self.update_interaction_sheets(interaction_results[-10:])
                        logger.info(f"已處理 {i + 1}/{len(target_article_ids)} 個Article")
                    
                    # 添加延遲避免API限制
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    logger.error(f"處理Article {article_id} 時發生錯誤: {e}")
                    failed_count += 1
            
            # 更新剩餘的數據
            if interaction_results:
                await self.update_interaction_sheets(interaction_results)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            return {
                "success": True,
                "message": f"刷新完成，處理了 {processed_count} 個Article，失敗 {failed_count} 個",
                "task_id": task_id,
                "total_articles": len(target_article_ids),
                "processed_articles": processed_count,
                "failed_articles": failed_count,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_seconds": duration
            }
            
        except Exception as e:
            logger.error(f"刷新互動數據失敗: {e}")
            return {
                "success": False,
                "message": f"刷新失敗: {str(e)}",
                "task_id": task_id,
                "total_articles": len(target_article_ids) if 'target_article_ids' in locals() else 0,
                "processed_articles": processed_count if 'processed_count' in locals() else 0,
                "failed_articles": failed_count if 'failed_count' in locals() else 0,
                "start_time": start_time.isoformat()
            }

# 創建服務實例
refresh_service = InteractionRefreshService()

@router.post("/refresh", response_model=RefreshResponse)
async def refresh_interactions(
    request: RefreshRequest,
    background_tasks: BackgroundTasks
):
    """
    刷新所有歷史Article ID的互動數據
    
    Args:
        request: 刷新請求參數
        background_tasks: 背景任務
        
    Returns:
        刷新響應
    """
    try:
        # 在背景任務中執行刷新
        task_id = f"refresh_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 啟動背景任務
        background_tasks.add_task(
            refresh_service.refresh_all_interactions,
            request.force_refresh,
            request.article_ids
        )
        
        return RefreshResponse(
            success=True,
            message="刷新任務已啟動，請稍後查看結果",
            task_id=task_id,
            start_time=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"啟動刷新任務失敗: {e}")
        raise HTTPException(status_code=500, detail=f"啟動刷新任務失敗: {str(e)}")

@router.get("/refresh/status/{task_id}")
async def get_refresh_status(task_id: str):
    """
    獲取刷新任務狀態
    
    Args:
        task_id: 任務ID
        
    Returns:
        任務狀態
    """
    try:
        # 這裡可以實現任務狀態查詢邏輯
        # 目前返回基本狀態
        return {
            "task_id": task_id,
            "status": "running",  # running, completed, failed
            "message": "任務執行中..."
        }
        
    except Exception as e:
        logger.error(f"獲取任務狀態失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取任務狀態失敗: {str(e)}")

@router.get("/articles")
async def get_article_list():
    """
    獲取所有Article ID列表
    
    Returns:
        Article ID列表
    """
    try:
        article_ids = await refresh_service.get_all_article_ids()
        return {
            "success": True,
            "total_count": len(article_ids),
            "article_ids": article_ids
        }
        
    except Exception as e:
        logger.error(f"獲取Article列表失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取Article列表失敗: {str(e)}")

























