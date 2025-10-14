#!/usr/bin/env python3
"""
定時發文系統 - 每隔一分鐘發兩篇
"""
import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any
from src.core.main_workflow_engine import MainWorkflowEngine

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScheduledPublisher:
    """定時發文器"""
    
    def __init__(self):
        self.workflow_engine = MainWorkflowEngine()
        self.published_count = 0
        self.target_count = 4  # 先發四篇
        
    async def publish_posts(self, posts_per_batch: int = 2):
        """發文批次"""
        try:
            logger.info(f"🚀 開始第 {self.published_count + 1} 批次發文...")
            
            # 獲取待發文的貼文列表
            posts_to_publish = await self.get_posts_to_publish(posts_per_batch)
            
            if not posts_to_publish:
                logger.warning("⚠️ 沒有待發文的貼文")
                return False
            
            # 發文
            for post in posts_to_publish:
                success = await self.publish_single_post(post)
                if success:
                    self.published_count += 1
                    logger.info(f"✅ 第 {self.published_count} 篇發文成功: {post['post_id']}")
                else:
                    logger.error(f"❌ 發文失敗: {post['post_id']}")
            
            logger.info(f"📊 本批次完成，已發文 {self.published_count}/{self.target_count} 篇")
            return True
            
        except Exception as e:
            logger.error(f"❌ 批次發文失敗: {e}")
            return False
    
    async def get_posts_to_publish(self, count: int) -> List[Dict[str, Any]]:
        """獲取待發文的貼文"""
        try:
            # 從 Google Sheets 讀取 ready_to_post 狀態的貼文
            posts = []
            
            # 模擬從 Google Sheets 讀取數據
            # 實際應該調用 Google Sheets API
            mock_posts = [
                {
                    'post_id': f'batch_{datetime.now().strftime("%Y%m%d_%H%M%S")}_001',
                    'kol_serial': 'kol_201',
                    'kol_nickname': '情緒派',
                    'title': '昇佳電子(6732) 月營收驚喜！情緒派韭菜們準備好了嗎？',
                    'content': '大家快來看！昇佳電子(6732)在 2024 年 12 月的月營收報告出爐啦！這次的營收數字讓人眼睛為之一亮...',
                    'stock_id': '6732',
                    'stock_name': '昇佳電子'
                },
                {
                    'post_id': f'batch_{datetime.now().strftime("%Y%m%d_%H%M%S")}_002',
                    'kol_serial': 'kol_202',
                    'kol_nickname': '技術派',
                    'title': '立積(4968) 月營收大解析！財務狀況暢旺📈',
                    'content': '立積(4968)在 2024 年 12 月份的營收數字可謂是相當亮眼，達到了 1000000 元！',
                    'stock_id': '4968',
                    'stock_name': '立積'
                }
            ]
            
            return mock_posts[:count]
            
        except Exception as e:
            logger.error(f"❌ 獲取待發文貼文失敗: {e}")
            return []
    
    async def publish_single_post(self, post: Dict[str, Any]) -> bool:
        """發文單篇貼文"""
        try:
            logger.info(f"📝 準備發文: {post['title'][:30]}...")
            logger.info(f"🎯 KOL: {post['kol_nickname']}")
            logger.info(f"📈 股票: {post['stock_name']}({post['stock_id']})")
            
            # 模擬發文過程
            await asyncio.sleep(2)  # 模擬發文時間
            
            # 更新發文狀態
            await self.update_post_status(post['post_id'], 'published')
            
            logger.info(f"✅ 發文成功: {post['post_id']}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 發文失敗: {e}")
            return False
    
    async def update_post_status(self, post_id: str, status: str):
        """更新貼文狀態"""
        try:
            # 這裡應該調用 Google Sheets API 更新狀態
            logger.info(f"📋 更新貼文狀態: {post_id} -> {status}")
            
        except Exception as e:
            logger.error(f"❌ 更新狀態失敗: {e}")
    
    async def run_scheduled_publishing(self, interval_minutes: int = 1):
        """運行定時發文"""
        try:
            logger.info(f"⏰ 開始定時發文系統")
            logger.info(f"📊 目標發文數: {self.target_count}")
            logger.info(f"⏱️ 發文間隔: {interval_minutes} 分鐘")
            logger.info(f"📦 每批次: 2 篇")
            
            while self.published_count < self.target_count:
                current_time = datetime.now()
                logger.info(f"🕐 當前時間: {current_time.strftime('%H:%M:%S')}")
                
                # 發文
                success = await self.publish_posts(2)
                
                if not success:
                    logger.warning("⚠️ 本批次發文失敗，等待下次嘗試")
                
                # 檢查是否完成
                if self.published_count >= self.target_count:
                    logger.info(f"🎉 完成所有發文目標！共發文 {self.published_count} 篇")
                    break
                
                # 等待下一批次
                if self.published_count < self.target_count:
                    logger.info(f"⏳ 等待 {interval_minutes} 分鐘後進行下一批次...")
                    await asyncio.sleep(interval_minutes * 60)
            
            logger.info("✅ 定時發文系統完成")
            
        except Exception as e:
            logger.error(f"❌ 定時發文系統失敗: {e}")

async def main():
    """主函數"""
    try:
        publisher = ScheduledPublisher()
        await publisher.run_scheduled_publishing(interval_minutes=1)
        
    except Exception as e:
        logger.error(f"❌ 主程序失敗: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())

























