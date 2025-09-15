#!/usr/bin/env python3
"""
發文後處理模組
處理發文後的數據收集、Article ID 追蹤和自我學習機制
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class PostResult:
    """發文結果"""
    post_id: str
    kol_serial: str
    article_id: str
    platform_url: str
    publish_time: datetime
    success: bool
    error_message: str = ""

@dataclass
class InteractionData:
    """互動數據"""
    article_id: str
    kol_serial: str
    like_count: int
    comment_count: int
    share_count: int
    view_count: int
    engagement_rate: float
    collection_time: datetime

class PostProcessingManager:
    """發文後處理管理器"""
    
    def __init__(self, workflow_engine):
        """初始化發文後處理管理器"""
        self.workflow_engine = workflow_engine
        self.post_results: List[PostResult] = []
        self.interaction_data: List[InteractionData] = []
        
        logger.info("發文後處理管理器初始化完成")
    
    async def process_post_result(self, post_result: PostResult):
        """處理發文結果"""
        try:
            # 1. 記錄發文結果
            self.post_results.append(post_result)
            
            # 2. 如果發文成功，添加到 Article ID 追蹤器
            if post_result.success and post_result.article_id:
                await self.workflow_engine.add_article_to_tracker(
                    post_result.kol_serial, 
                    post_result.article_id
                )
                
                # 3. 更新 Google Sheets 中的發文狀態
                await self._update_post_status_in_sheets(post_result)
                
                logger.info(f"✅ 發文成功處理: {post_result.post_id} -> {post_result.article_id}")
            else:
                logger.warning(f"⚠️ 發文失敗: {post_result.post_id} - {post_result.error_message}")
                
        except Exception as e:
            logger.error(f"處理發文結果失敗: {e}")
    
    async def _update_post_status_in_sheets(self, post_result: PostResult):
        """更新 Google Sheets 中的發文狀態"""
        try:
            # 使用新的 Google Sheets ID
            new_sheets_id = os.getenv('GOOGLE_SHEETS_ID')
            
            # 創建新的 Google Sheets 客戶端
            from src.clients.google.sheets_client import GoogleSheetsClient
            new_sheets_client = GoogleSheetsClient(
                credentials_file=self.workflow_engine.config.google.credentials_file,
                spreadsheet_id=new_sheets_id
            )
            
            # 更新發文狀態欄位
            update_data = {
                'publish_status': 'published',
                'platform_post_id': post_result.article_id,
                'platform_post_url': post_result.platform_url,
                'articleid': post_result.article_id,
                'publish_time': post_result.publish_time.isoformat()
            }
            
            # 這裡需要實現根據 post_id 找到對應行並更新的邏輯
            # 暫時記錄到日誌
            logger.info(f"📝 更新發文狀態: {post_result.post_id} -> {update_data}")
            
        except Exception as e:
            logger.error(f"更新 Google Sheets 發文狀態失敗: {e}")
    
    async def collect_interaction_data(self, kol_serial: str, article_ids: List[str]):
        """收集互動數據"""
        try:
            logger.info(f"開始收集 KOL {kol_serial} 的互動數據...")
            
            for article_id in article_ids:
                try:
                    # 這裡應該調用 CMoney API 獲取互動數據
                    interaction_data = await self._fetch_interaction_data(article_id, kol_serial)
                    
                    if interaction_data:
                        self.interaction_data.append(interaction_data)
                        logger.info(f"✅ 收集到互動數據: {article_id}")
                    
                    # 避免 API 限制
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    logger.error(f"收集文章 {article_id} 互動數據失敗: {e}")
            
            logger.info(f"完成收集 KOL {kol_serial} 的互動數據，共 {len(article_ids)} 篇文章")
            
        except Exception as e:
            logger.error(f"收集互動數據失敗: {e}")
    
    async def _fetch_interaction_data(self, article_id: str, kol_serial: str) -> Optional[InteractionData]:
        """從 CMoney API 獲取互動數據"""
        try:
            # 這裡應該實現實際的 API 調用
            # 暫時返回模擬數據
            import random
            
            return InteractionData(
                article_id=article_id,
                kol_serial=kol_serial,
                like_count=random.randint(10, 100),
                comment_count=random.randint(5, 50),
                share_count=random.randint(2, 20),
                view_count=random.randint(100, 1000),
                engagement_rate=random.uniform(0.05, 0.15),
                collection_time=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"獲取互動數據失敗: {e}")
            return None
    
    async def save_interaction_data_to_sheets(self):
        """保存互動數據到 Google Sheets"""
        try:
            if not self.interaction_data:
                logger.info("沒有互動數據需要保存")
                return
            
            # 使用新的 Google Sheets ID
            new_sheets_id = os.getenv('GOOGLE_SHEETS_ID')
            
            # 創建新的 Google Sheets 客戶端
            from src.clients.google.sheets_client import GoogleSheetsClient
            new_sheets_client = GoogleSheetsClient(
                credentials_file=self.workflow_engine.config.google.credentials_file,
                spreadsheet_id=new_sheets_id
            )
            
            # 準備互動數據
            interaction_rows = []
            for data in self.interaction_data:
                row = [
                    data.article_id,
                    data.kol_serial,
                    str(data.like_count),
                    str(data.comment_count),
                    str(data.share_count),
                    str(data.view_count),
                    str(data.engagement_rate),
                    data.collection_time.isoformat()
                ]
                interaction_rows.append(row)
            
            # 寫入到互動數據工作表
            await new_sheets_client.append_sheet('互動數據', interaction_rows)
            
            logger.info(f"✅ 保存 {len(self.interaction_data)} 筆互動數據到 Google Sheets")
            
        except Exception as e:
            logger.error(f"保存互動數據到 Google Sheets 失敗: {e}")
    
    async def execute_learning_cycle(self):
        """執行學習週期"""
        try:
            logger.info("開始執行學習週期...")
            
            # 1. 分析互動數據
            await self._analyze_interaction_patterns()
            
            # 2. 更新 KOL 學習分數
            await self._update_kol_learning_scores()
            
            # 3. 生成學習洞察
            await self._generate_learning_insights()
            
            # 4. 保存學習結果
            await self._save_learning_results()
            
            logger.info("學習週期執行完成")
            
        except Exception as e:
            logger.error(f"執行學習週期失敗: {e}")
    
    async def _analyze_interaction_patterns(self):
        """分析互動模式"""
        try:
            if not self.interaction_data:
                logger.info("沒有互動數據可供分析")
                return
            
            # 按 KOL 分組分析
            kol_interactions = {}
            for data in self.interaction_data:
                if data.kol_serial not in kol_interactions:
                    kol_interactions[data.kol_serial] = []
                kol_interactions[data.kol_serial].append(data)
            
            # 分析每個 KOL 的表現
            for kol_serial, interactions in kol_interactions.items():
                avg_engagement = sum(data.engagement_rate for data in interactions) / len(interactions)
                total_likes = sum(data.like_count for data in interactions)
                total_comments = sum(data.comment_count for data in interactions)
                
                logger.info(f"KOL {kol_serial} 分析結果:")
                logger.info(f"  平均互動率: {avg_engagement:.2%}")
                logger.info(f"  總讚數: {total_likes}")
                logger.info(f"  總留言數: {total_comments}")
                
        except Exception as e:
            logger.error(f"分析互動模式失敗: {e}")
    
    async def _update_kol_learning_scores(self):
        """更新 KOL 學習分數"""
        try:
            # 這裡應該實現實際的學習分數更新邏輯
            logger.info("更新 KOL 學習分數...")
            
        except Exception as e:
            logger.error(f"更新 KOL 學習分數失敗: {e}")
    
    async def _generate_learning_insights(self):
        """生成學習洞察"""
        try:
            # 這裡應該實現實際的學習洞察生成邏輯
            logger.info("生成學習洞察...")
            
        except Exception as e:
            logger.error(f"生成學習洞察失敗: {e}")
    
    async def _save_learning_results(self):
        """保存學習結果"""
        try:
            # 這裡應該實現實際的學習結果保存邏輯
            logger.info("保存學習結果...")
            
        except Exception as e:
            logger.error(f"保存學習結果失敗: {e}")
    
    def get_post_summary(self) -> Dict[str, Any]:
        """獲取發文摘要"""
        total_posts = len(self.post_results)
        successful_posts = len([p for p in self.post_results if p.success])
        failed_posts = total_posts - successful_posts
        
        return {
            'total_posts': total_posts,
            'successful_posts': successful_posts,
            'failed_posts': failed_posts,
            'success_rate': successful_posts / total_posts if total_posts > 0 else 0,
            'total_interactions': len(self.interaction_data)
        }



