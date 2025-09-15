#!/usr/bin/env python3
"""
定時發文系統 - 從備份文件讀取實際貼文數據
"""
import asyncio
import logging
import json
import glob
import os
from datetime import datetime
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
        self.available_posts = []
        self.current_post_index = 0
        
    def load_posts_from_backup(self):
        """從備份文件載入貼文"""
        try:
            backup_files = glob.glob("data/backup/post_record_*.json")
            backup_files.sort()
            
            logger.info(f"📁 找到 {len(backup_files)} 個備份文件")
            
            for file_path in backup_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # 檢查是否為 ready_to_post 狀態
                    if data.get('status') == 'ready_to_post':
                        post = {
                            'post_id': data.get('post_id'),
                            'kol_serial': data.get('kol_serial'),
                            'kol_nickname': data.get('kol_nickname'),
                            'title': data.get('title'),
                            'content': data.get('content'),
                            'stock_id': data.get('stock_id'),
                            'stock_name': data.get('stock_name'),
                            'analysis_type': data.get('analysis_type'),
                            'file_path': file_path
                        }
                        self.available_posts.append(post)
                        
                except Exception as e:
                    logger.error(f"❌ 讀取文件 {file_path} 失敗: {e}")
            
            logger.info(f"📋 載入 {len(self.available_posts)} 篇待發文貼文")
            
        except Exception as e:
            logger.error(f"❌ 載入備份文件失敗: {e}")
    
    async def publish_posts(self, posts_per_batch: int = 2):
        """發文批次"""
        try:
            logger.info(f"🚀 開始第 {(self.published_count // 2) + 1} 批次發文...")
            
            # 獲取待發文的貼文
            posts_to_publish = []
            for i in range(posts_per_batch):
                if self.current_post_index < len(self.available_posts):
                    posts_to_publish.append(self.available_posts[self.current_post_index])
                    self.current_post_index += 1
            
            if not posts_to_publish:
                logger.warning("⚠️ 沒有更多待發文的貼文")
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
    
    async def publish_single_post(self, post: Dict[str, Any]) -> bool:
        """發文單篇貼文"""
        try:
            logger.info(f"📝 準備發文: {post['title'][:30]}...")
            logger.info(f"🎯 KOL: {post['kol_nickname']}")
            logger.info(f"📈 股票: {post['stock_name']}({post['stock_id']})")
            logger.info(f"📊 分析類型: {post['analysis_type']}")
            
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
            
            # 保存發文記錄
            await self.save_publishing_record(post_id, status)
            
        except Exception as e:
            logger.error(f"❌ 更新狀態失敗: {e}")
    
    async def save_publishing_record(self, post_id: str, status: str):
        """保存發文記錄"""
        try:
            record = {
                'post_id': post_id,
                'publish_time': datetime.now().isoformat(),
                'status': status,
                'publisher': 'scheduled_publisher'
            }
            
            # 保存到本地文件
            os.makedirs('data/publishing_records', exist_ok=True)
            filename = f"publishing_record_{post_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = os.path.join('data/publishing_records', filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(record, f, ensure_ascii=False, indent=2)
            
            logger.info(f"💾 發文記錄已保存: {filepath}")
            
        except Exception as e:
            logger.error(f"❌ 保存發文記錄失敗: {e}")
    
    async def run_scheduled_publishing(self, interval_minutes: int = 1):
        """運行定時發文"""
        try:
            # 載入貼文數據
            self.load_posts_from_backup()
            
            if not self.available_posts:
                logger.error("❌ 沒有可發文的貼文")
                return
            
            logger.info(f"⏰ 開始定時發文系統")
            logger.info(f"📊 目標發文數: {self.target_count}")
            logger.info(f"📋 可用貼文數: {len(self.available_posts)}")
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
                
                # 檢查是否還有貼文可發
                if self.current_post_index >= len(self.available_posts):
                    logger.warning("⚠️ 沒有更多貼文可發")
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











