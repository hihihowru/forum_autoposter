#!/usr/bin/env python3
"""
盤中漲停機器人
接收股票代號列表，自動生成漲停分析內容並發文
"""

import asyncio
import sys
import os
from typing import List
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.clients.google.sheets_client import GoogleSheetsClient
from src.services.flow.unified_flow_manager import create_unified_flow_manager, FlowConfig
from src.utils.limit_up_data_parser import LimitUpDataParser

class IntradayLimitUpBot:
    """盤中漲停機器人"""
    
    def __init__(self):
        """初始化機器人"""
        self.sheets_client = GoogleSheetsClient(
            credentials_file="./credentials/google-service-account.json",
            spreadsheet_id="148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LikN2s"
        )
        self.flow_manager = create_unified_flow_manager(self.sheets_client)
        self.limit_up_parser = LimitUpDataParser()
        
        print("🤖 盤中漲停機器人初始化完成")
    
    async def process_stock_list(self, stock_ids: List[str], 
                               max_assignments_per_topic: int = 2,
                               enable_content_generation: bool = True,
                               enable_sheets_recording: bool = True,
                               enable_publishing: bool = False) -> dict:
        """
        處理股票代號列表
        
        Args:
            stock_ids: 股票代號列表，例如 ["2330", "2317", "2454"]
            max_assignments_per_topic: 每個話題最多分派幾個 KOL
            enable_content_generation: 是否生成內容
            enable_sheets_recording: 是否記錄到 Google Sheets
            enable_publishing: 是否實際發文
            
        Returns:
            處理結果
        """
        print(f"\n🚀 開始處理股票列表: {stock_ids}")
        print("=" * 60)
        
        # 配置流程
        config = FlowConfig(
            flow_type="intraday_limit_up",
            max_assignments_per_topic=max_assignments_per_topic,
            enable_stock_analysis=True,
            enable_content_generation=enable_content_generation,
            enable_sheets_recording=enable_sheets_recording,
            enable_publishing=enable_publishing
        )
        
        # 執行盤中漲停流程
        result = await self.flow_manager.execute_intraday_limit_up_flow(stock_ids, config)
        
        # 顯示結果
        print(f"\n📊 處理結果:")
        print(f"   成功: {'✅' if result.success else '❌'}")
        print(f"   流程類型: {result.flow_type}")
        print(f"   處理話題數: {result.processed_topics}")
        print(f"   生成貼文數: {result.generated_posts}")
        print(f"   執行時間: {result.execution_time:.2f}秒")
        print(f"   錯誤數: {len(result.errors)}")
        
        if result.errors:
            print(f"\n❌ 錯誤詳情:")
            for error in result.errors:
                print(f"   - {error}")
        
        return {
            'success': result.success,
            'processed_topics': result.processed_topics,
            'generated_posts': result.generated_posts,
            'execution_time': result.execution_time,
            'errors': result.errors
        }
    
    async def process_limit_up_data(self, limit_up_data: str,
                                  max_assignments_per_topic: int = 2,
                                  enable_content_generation: bool = True,
                                  enable_sheets_recording: bool = True,
                                  enable_publishing: bool = False) -> dict:
        """
        處理漲停資料
        
        Args:
            limit_up_data: 漲停排行資料文字
            max_assignments_per_topic: 每個話題最多分派幾個 KOL
            enable_content_generation: 是否生成內容
            enable_sheets_recording: 是否記錄到 Google Sheets
            enable_publishing: 是否實際發文
            
        Returns:
            處理結果
        """
        print(f"\n📈 開始處理漲停資料")
        print("=" * 60)
        
        # 1. 解析漲停資料
        print("🔍 解析漲停資料...")
        stock_data_list = self.limit_up_parser.parse_limit_up_data(limit_up_data)
        
        if not stock_data_list:
            print("❌ 無法解析漲停資料")
            return {
                'success': False,
                'processed_topics': 0,
                'generated_posts': 0,
                'execution_time': 0,
                'errors': ['無法解析漲停資料']
            }
        
        print(f"✅ 解析完成，共 {len(stock_data_list)} 檔股票")
        
        # 2. 提取股票代號
        stock_ids = [stock_data['stock_id'] for stock_data in stock_data_list if stock_data.get('stock_id')]
        
        if not stock_ids:
            print("❌ 無法提取股票代號")
            return {
                'success': False,
                'processed_topics': 0,
                'generated_posts': 0,
                'execution_time': 0,
                'errors': ['無法提取股票代號']
            }
        
        print(f"📊 提取股票代號: {stock_ids}")
        
        # 3. 將漲停資料載入到流程管理器的解析器中
        self.flow_manager.limit_up_parser = self.limit_up_parser
        
        # 4. 執行盤中漲停流程
        return await self.process_stock_list(
            stock_ids=stock_ids,
            max_assignments_per_topic=max_assignments_per_topic,
            enable_content_generation=enable_content_generation,
            enable_sheets_recording=enable_sheets_recording,
            enable_publishing=enable_publishing
        )
    
    async def run_interactive_mode(self):
        """互動模式"""
        print("🤖 盤中漲停機器人 - 互動模式")
        print("=" * 60)
        
        while True:
            try:
                # 獲取股票代號列表
                print("\n📈 請輸入股票代號列表（用逗號分隔，例如: 2330,2317,2454）")
                print("輸入 'quit' 退出")
                
                user_input = input("股票代號: ").strip()
                
                if user_input.lower() == 'quit':
                    print("👋 再見！")
                    break
                
                if not user_input:
                    print("❌ 請輸入股票代號")
                    continue
                
                # 解析股票代號
                stock_ids = [stock_id.strip() for stock_id in user_input.split(',')]
                
                # 配置選項
                print("\n⚙️ 配置選項:")
                max_assignments = input("每個話題最多分派幾個 KOL (預設: 2): ").strip()
                max_assignments = int(max_assignments) if max_assignments.isdigit() else 2
                
                enable_content = input("是否生成內容 (y/n, 預設: y): ").strip().lower()
                enable_content = enable_content != 'n'
                
                enable_sheets = input("是否記錄到 Google Sheets (y/n, 預設: y): ").strip().lower()
                enable_sheets = enable_sheets != 'n'
                
                enable_publish = input("是否實際發文 (y/n, 預設: n): ").strip().lower()
                enable_publish = enable_publish == 'y'
                
                # 處理股票列表
                result = await self.process_stock_list(
                    stock_ids=stock_ids,
                    max_assignments_per_topic=max_assignments,
                    enable_content_generation=enable_content,
                    enable_sheets_recording=enable_sheets,
                    enable_publishing=enable_publish
                )
                
                if result['success']:
                    print(f"\n🎉 處理完成！生成 {result['generated_posts']} 篇貼文")
                else:
                    print(f"\n❌ 處理失敗，請檢查錯誤訊息")
                
            except KeyboardInterrupt:
                print("\n👋 再見！")
                break
            except Exception as e:
                print(f"\n❌ 發生錯誤: {e}")
                continue

async def main():
    """主函數"""
    # 檢查是否提供股票代號參數
    if len(sys.argv) > 1:
        # 命令行模式
        stock_ids = sys.argv[1:]
        print(f"📈 命令行模式，股票代號: {stock_ids}")
        
        bot = IntradayLimitUpBot()
        result = await bot.process_stock_list(stock_ids)
        
        if result['success']:
            print(f"🎉 處理完成！生成 {result['generated_posts']} 篇貼文")
        else:
            print(f"❌ 處理失敗")
            sys.exit(1)
    else:
        # 互動模式
        bot = IntradayLimitUpBot()
        await bot.run_interactive_mode()

if __name__ == "__main__":
    asyncio.run(main())
