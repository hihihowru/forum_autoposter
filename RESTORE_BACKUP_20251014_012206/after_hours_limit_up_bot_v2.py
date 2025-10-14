#!/usr/bin/env python3
"""
盤後機器人發文腳本 - 使用統一觸發器接口
固定KOL池分配策略，每檔股票分配1個KOL
"""

import os
import sys
import asyncio
import logging
from datetime import datetime
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.services.flow.unified_trigger_interface import UnifiedTriggerInterface, execute_after_hours_limit_up
from src.services.flow.kol_allocation_strategy import TriggerConfig, AllocationStrategy

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AfterHoursLimitUpBot:
    """盤後漲停股機器人"""
    
    def __init__(self):
        self.trigger_interface = UnifiedTriggerInterface()
        logger.info("盤後機器人初始化完成")
    
    async def run_after_hours_bot(self):
        """執行盤後機器人"""
        print("🚀 盤後漲停股機器人啟動")
        print("=" * 60)
        print(f"⏰ 開始時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # 使用統一觸發器接口執行
            result = await execute_after_hours_limit_up()
            
            if result.success:
                print(f"\n✅ 盤後機器人執行成功!")
                print(f"📊 處理話題數: {result.total_topics}")
                print(f"👥 分配任務數: {result.total_assignments}")
                print(f"📝 生成貼文數: {result.generated_posts}")
                print(f"⏱️ 執行時間: {result.execution_time:.2f} 秒")
                print(f"🎯 分配策略: {result.allocation_strategy}")
                
                # 顯示詳細資訊
                if result.details:
                    print(f"\n📋 詳細資訊:")
                    print(f"   API調配: {result.details.get('api_allocation', {})}")
                    print(f"   KOL分配: {result.details.get('kol_allocation', {})}")
                
                # 顯示生成的貼文預覽
                generated_posts = result.details.get('generated_posts', [])
                if generated_posts:
                    print(f"\n📄 生成貼文預覽 (前3篇):")
                    for i, post in enumerate(generated_posts[:3], 1):
                        print(f"{i}. {post.get('kol_nickname', 'Unknown')}: {post.get('title', '無標題')}")
                        print(f"   內容預覽: {post.get('content', '無內容')[:100]}...")
                        print()
                
                print(f"\n🔗 請檢查 Google Sheets 查看完整記錄")
                print(f"   📋 貼文記錄表: https://docs.google.com/spreadsheets/d/{os.getenv('GOOGLE_SHEETS_ID')}/edit#gid=0")
                
            else:
                print(f"\n❌ 盤後機器人執行失敗")
                print(f"錯誤列表:")
                for error in result.errors:
                    print(f"  - {error}")
                
        except Exception as e:
            print(f"❌ 盤後機器人執行異常: {e}")
            logger.error(f"盤後機器人執行失敗: {e}")
            import traceback
            traceback.print_exc()
        
        print(f"\n⏰ 結束時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
    
    def update_kol_pool(self, new_kol_list: list):
        """更新固定KOL池"""
        try:
            # 更新盤後機器人的固定KOL池
            self.trigger_interface.kol_allocation.update_fixed_pool(
                "after_hours_limit_up", 
                "all", 
                new_kol_list
            )
            print(f"✅ 已更新盤後機器人KOL池: {new_kol_list}")
        except Exception as e:
            print(f"❌ 更新KOL池失敗: {e}")
    
    def get_bot_status(self):
        """獲取機器人狀態"""
        try:
            summary = self.trigger_interface.get_trigger_summary()
            print("🤖 盤後機器人狀態:")
            print(f"   可用觸發器: {summary['available_triggers']}")
            print(f"   分配策略: {summary['allocation_strategies']}")
            print(f"   KOL配置: {summary['kol_allocation_summary']}")
        except Exception as e:
            print(f"❌ 獲取狀態失敗: {e}")

async def main():
    """主函數"""
    bot = AfterHoursLimitUpBot()
    
    # 顯示機器人狀態
    bot.get_bot_status()
    print()
    
    # 執行盤後機器人
    await bot.run_after_hours_bot()

if __name__ == "__main__":
    asyncio.run(main())










