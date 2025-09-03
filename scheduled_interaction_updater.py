#!/usr/bin/env python3
"""
定時更新即時互動數據腳本
可以設定定時執行，持續更新貼文的即時互動數據
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from update_realtime_interactions import RealtimeInteractionUpdater

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ScheduledInteractionUpdater:
    """定時互動數據更新器"""
    
    def __init__(self, interval_minutes: int = 30):
        """
        初始化定時更新器
        
        Args:
            interval_minutes: 更新間隔（分鐘）
        """
        self.interval_minutes = interval_minutes
        self.updater = RealtimeInteractionUpdater()
        self.is_running = False
        self.last_run_time = None
    
    async def run_update_cycle(self):
        """執行一次更新週期"""
        try:
            logger.info("🔄 開始執行互動數據更新週期")
            await self.updater.run()
            self.last_run_time = datetime.now()
            logger.info("✅ 互動數據更新週期完成")
        except Exception as e:
            logger.error(f"❌ 更新週期失敗: {e}")
    
    async def start(self):
        """啟動定時更新服務"""
        logger.info(f"🚀 啟動定時互動數據更新服務，間隔: {self.interval_minutes} 分鐘")
        self.is_running = True
        
        while self.is_running:
            try:
                # 檢查是否應該運行
                now = datetime.now()
                if (self.last_run_time is None or 
                    now - self.last_run_time >= timedelta(minutes=self.interval_minutes)):
                    
                    await self.run_update_cycle()
                else:
                    # 等待到下次運行時間
                    next_run = self.last_run_time + timedelta(minutes=self.interval_minutes)
                    wait_seconds = (next_run - now).total_seconds()
                    logger.info(f"⏰ 等待 {wait_seconds/60:.1f} 分鐘到下次更新")
                    await asyncio.sleep(min(wait_seconds, 300))  # 最多等待5分鐘
                    
            except KeyboardInterrupt:
                logger.info("🛑 收到停止信號，正在關閉服務...")
                self.is_running = False
                break
            except Exception as e:
                logger.error(f"❌ 服務運行異常: {e}")
                await asyncio.sleep(60)  # 異常時等待1分鐘
        
        logger.info("✅ 定時互動數據更新服務已停止")
    
    def stop(self):
        """停止服務"""
        self.is_running = False

async def main():
    """主函數"""
    import sys
    
    # 從命令行參數獲取更新間隔
    interval_minutes = 30  # 預設30分鐘
    if len(sys.argv) > 1:
        try:
            interval_minutes = int(sys.argv[1])
        except ValueError:
            logger.warning(f"無效的間隔參數: {sys.argv[1]}，使用預設值: {interval_minutes} 分鐘")
    
    # 創建並啟動定時更新器
    updater = ScheduledInteractionUpdater(interval_minutes=interval_minutes)
    
    try:
        await updater.start()
    except KeyboardInterrupt:
        logger.info("收到中斷信號，正在停止服務...")
        updater.stop()

if __name__ == "__main__":
    asyncio.run(main())
