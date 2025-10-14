#!/usr/bin/env python3
"""
KOL 配置管理腳本
用於設定新的KOL帳密和分配策略
"""

import os
import sys
import asyncio
import json
from datetime import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.services.flow.unified_trigger_interface import UnifiedTriggerInterface
from src.services.flow.kol_allocation_strategy import TriggerConfig, AllocationStrategy

class KOLConfigManager:
    """KOL配置管理器"""
    
    def __init__(self):
        self.trigger_interface = UnifiedTriggerInterface()
        print("✅ KOL配置管理器初始化完成")
    
    def setup_new_kol_pool(self, trigger_type: str, kol_list: List[int], pool_name: str = "all"):
        """
        設定新的KOL池
        
        Args:
            trigger_type: 觸發器類型 (after_hours_limit_up, intraday_surge, trending_topics)
            kol_list: KOL序號列表
            pool_name: 池子名稱
        """
        try:
            # 更新固定KOL池
            self.trigger_interface.kol_allocation.update_fixed_pool(
                trigger_type, pool_name, kol_list
            )
            
            print(f"✅ 已設定 {trigger_type} 的 {pool_name} KOL池:")
            print(f"   KOL列表: {kol_list}")
            print(f"   總數: {len(kol_list)} 個KOL")
            
        except Exception as e:
            print(f"❌ 設定KOL池失敗: {e}")
    
    def setup_after_hours_kol_pool(self, high_volume_kols: List[int], low_volume_kols: List[int]):
        """
        設定盤後機器人的KOL池
        
        Args:
            high_volume_kols: 高量股票專用KOL (建議5個)
            low_volume_kols: 低量股票專用KOL (建議5個)
        """
        print("🎯 設定盤後機器人KOL池")
        print("=" * 50)
        
        # 設定高量股票KOL池
        self.setup_new_kol_pool("after_hours_limit_up", high_volume_kols, "high_volume")
        
        # 設定低量股票KOL池  
        self.setup_new_kol_pool("after_hours_limit_up", low_volume_kols, "low_volume")
        
        # 合併池子用於總體分配
        all_kols = high_volume_kols + low_volume_kols
        self.setup_new_kol_pool("after_hours_limit_up", all_kols, "all")
        
        print(f"\n📊 盤後機器人KOL池設定完成:")
        print(f"   高量股票KOL: {high_volume_kols} ({len(high_volume_kols)}個)")
        print(f"   低量股票KOL: {low_volume_kols} ({len(low_volume_kols)}個)")
        print(f"   總計KOL: {all_kols} ({len(all_kols)}個)")
    
    def setup_intraday_kol_pool(self, kol_list: List[int]):
        """設定盤中急漲股KOL池"""
        print("🎯 設定盤中急漲股KOL池")
        print("=" * 50)
        
        self.setup_new_kol_pool("intraday_surge", kol_list, "all")
        
        print(f"📊 盤中急漲股KOL池設定完成:")
        print(f"   KOL列表: {kol_list} ({len(kol_list)}個)")
    
    def update_trigger_strategy(self, trigger_type: str, strategy: AllocationStrategy, max_assignments: int = 3):
        """
        更新觸發器分配策略
        
        Args:
            trigger_type: 觸發器類型
            strategy: 分配策略 (FIXED_POOL 或 MATCHING_POOL)
            max_assignments: 每個話題最大分配數
        """
        try:
            config = TriggerConfig(
                trigger_type=trigger_type,
                allocation_strategy=strategy,
                max_assignments_per_topic=max_assignments,
                enable_content_generation=True,
                enable_publishing=False
            )
            
            self.trigger_interface.update_trigger_config(trigger_type, config)
            
            print(f"✅ 已更新觸發器策略:")
            print(f"   觸發器: {trigger_type}")
            print(f"   策略: {strategy.value}")
            print(f"   最大分配數: {max_assignments}")
            
        except Exception as e:
            print(f"❌ 更新觸發器策略失敗: {e}")
    
    def show_current_config(self):
        """顯示當前配置"""
        print("📋 當前KOL配置")
        print("=" * 50)
        
        try:
            summary = self.trigger_interface.get_trigger_summary()
            
            print("🎯 可用觸發器:")
            for trigger in summary['available_triggers']:
                print(f"   - {trigger}")
            
            print(f"\n🎲 分配策略:")
            for strategy in summary['allocation_strategies']:
                print(f"   - {strategy}")
            
            print(f"\n👥 KOL配置摘要:")
            kol_summary = summary['kol_allocation_summary']
            print(f"   總KOL數: {kol_summary['total_kols']}")
            print(f"   固定池: {kol_summary['fixed_pools']}")
            
        except Exception as e:
            print(f"❌ 獲取配置失敗: {e}")
    
    def export_config(self, filename: str = None):
        """導出配置到文件"""
        if not filename:
            filename = f"kol_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            summary = self.trigger_interface.get_trigger_summary()
            
            config_data = {
                "export_time": datetime.now().isoformat(),
                "trigger_summary": summary,
                "environment_variables": {
                    "GOOGLE_SHEETS_ID": os.getenv('GOOGLE_SHEETS_ID'),
                    "GOOGLE_CREDENTIALS_FILE": os.getenv('GOOGLE_CREDENTIALS_FILE'),
                    "OPENAI_API_KEY": "***" if os.getenv('OPENAI_API_KEY') else None,
                    "FINLAB_API_KEY": "***" if os.getenv('FINLAB_API_KEY') else None,
                    "SERPER_API_KEY": "***" if os.getenv('SERPER_API_KEY') else None
                }
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 配置已導出到: {filename}")
            
        except Exception as e:
            print(f"❌ 導出配置失敗: {e}")

def main():
    """主函數 - 互動式配置"""
    manager = KOLConfigManager()
    
    print("🤖 KOL配置管理系統")
    print("=" * 60)
    
    while True:
        print("\n📋 請選擇操作:")
        print("1. 設定盤後機器人KOL池")
        print("2. 設定盤中急漲股KOL池")
        print("3. 更新觸發器策略")
        print("4. 顯示當前配置")
        print("5. 導出配置")
        print("6. 測試盤後機器人")
        print("0. 退出")
        
        choice = input("\n請輸入選項 (0-6): ").strip()
        
        if choice == "0":
            print("👋 再見!")
            break
        
        elif choice == "1":
            print("\n🎯 設定盤後機器人KOL池")
            print("請輸入KOL序號，用逗號分隔")
            
            high_volume_input = input("高量股票KOL (建議5個): ").strip()
            low_volume_input = input("低量股票KOL (建議5個): ").strip()
            
            try:
                high_volume_kols = [int(x.strip()) for x in high_volume_input.split(',') if x.strip()]
                low_volume_kols = [int(x.strip()) for x in low_volume_input.split(',') if x.strip()]
                
                manager.setup_after_hours_kol_pool(high_volume_kols, low_volume_kols)
                
            except ValueError:
                print("❌ 請輸入有效的數字")
        
        elif choice == "2":
            print("\n🎯 設定盤中急漲股KOL池")
            kol_input = input("KOL序號 (用逗號分隔): ").strip()
            
            try:
                kol_list = [int(x.strip()) for x in kol_input.split(',') if x.strip()]
                manager.setup_intraday_kol_pool(kol_list)
                
            except ValueError:
                print("❌ 請輸入有效的數字")
        
        elif choice == "3":
            print("\n🎲 更新觸發器策略")
            trigger_type = input("觸發器類型 (after_hours_limit_up/intraday_surge/trending_topics): ").strip()
            strategy_input = input("策略 (1=固定池, 2=配對池): ").strip()
            max_assignments = input("最大分配數 (預設3): ").strip()
            
            try:
                strategy = AllocationStrategy.FIXED_POOL if strategy_input == "1" else AllocationStrategy.MATCHING_POOL
                max_assignments = int(max_assignments) if max_assignments else 3
                
                manager.update_trigger_strategy(trigger_type, strategy, max_assignments)
                
            except ValueError:
                print("❌ 請輸入有效的數字")
        
        elif choice == "4":
            manager.show_current_config()
        
        elif choice == "5":
            filename = input("導出文件名 (按Enter使用預設): ").strip()
            manager.export_config(filename if filename else None)
        
        elif choice == "6":
            print("\n🚀 測試盤後機器人...")
            async def test_bot():
                from after_hours_limit_up_bot_v2 import AfterHoursLimitUpBot
                bot = AfterHoursLimitUpBot()
                await bot.run_after_hours_bot()
            
            asyncio.run(test_bot())
        
        else:
            print("❌ 無效選項，請重新選擇")

if __name__ == "__main__":
    main()






















