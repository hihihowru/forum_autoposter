#!/usr/bin/env python3
"""
盤後漲停觸發器完整流程數據檢查
檢查 FinLab API、Serper API、Google Sheets 更新等各環節
"""

import os
import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataCheckEngine:
    """數據檢查引擎"""
    
    def __init__(self):
        self.finlab_api_key = os.getenv('FINLAB_API_KEY')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.serper_api_key = os.getenv('SERPER_API_KEY')
        self.google_sheets_id = os.getenv('GOOGLE_SHEETS_ID')
        
        # 檢查 API 金鑰
        self._check_api_keys()
        
        logger.info("數據檢查引擎初始化完成")
    
    def _check_api_keys(self):
        """檢查 API 金鑰"""
        print("🔑 API 金鑰檢查")
        print("=" * 50)
        
        api_keys = {
            'FINLAB_API_KEY': self.finlab_api_key,
            'OPENAI_API_KEY': self.openai_api_key,
            'SERPER_API_KEY': self.serper_api_key
        }
        
        for key_name, key_value in api_keys.items():
            if key_value:
                print(f"✅ {key_name}: {'*' * 10}{key_value[-4:]}")
            else:
                print(f"❌ {key_name}: 未設置")
        
        print()
    
    async def check_finlab_api(self):
        """檢查 FinLab API"""
        print("📊 FinLab API 檢查")
        print("=" * 50)
        
        try:
            import finlab
            from finlab import data
            
            # 登入測試
            finlab.login(self.finlab_api_key)
            print("✅ FinLab 登入成功")
            
            # 測試數據表
            test_stock = '2330'
            test_tables = {
                '營收數據': 'monthly_revenue:當月營收',
                '財報數據': 'fundamental_features:每股稅後淨利',
                '股價數據': 'price:收盤價'
            }
            
            for table_name, table_key in test_tables.items():
                try:
                    data_source = data.get(table_key)
                    if data_source is not None and test_stock in data_source.columns:
                        stock_data = data_source[test_stock].dropna()
                        if len(stock_data) > 0:
                            print(f"✅ {table_name}: 可用，最新數據 {stock_data.index[-1]}")
                        else:
                            print(f"⚠️ {table_name}: 無數據")
                    else:
                        print(f"❌ {table_name}: 不可用")
                except Exception as e:
                    print(f"❌ {table_name}: 錯誤 - {e}")
            
        except Exception as e:
            print(f"❌ FinLab API 檢查失敗: {e}")
        
        print()
    
    async def check_serper_api(self):
        """檢查 Serper API"""
        print("🔍 Serper API 檢查")
        print("=" * 50)
        
        try:
            import httpx
            
            test_query = "台積電 2330 股票 新聞"
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://google.serper.dev/search",
                    headers={
                        "X-API-KEY": self.serper_api_key,
                        "Content-Type": "application/json"
                    },
                    json={
                        "q": test_query,
                        "num": 3
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    news_results = data.get('organic', [])
                    print(f"✅ Serper API 正常，獲取到 {len(news_results)} 則新聞")
                    
                    if news_results:
                        for i, result in enumerate(news_results[:2]):
                            title = result.get('title', '')
                            print(f"   {i+1}. {title[:50]}...")
                else:
                    print(f"❌ Serper API 錯誤: HTTP {response.status_code}")
                    
        except Exception as e:
            print(f"❌ Serper API 檢查失敗: {e}")
        
        print()
    
    async def check_openai_api(self):
        """檢查 OpenAI API"""
        print("🤖 OpenAI API 檢查")
        print("=" * 50)
        
        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=self.openai_api_key)
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "你是一個測試助手。"},
                    {"role": "user", "content": "請回覆 'API 測試成功'"}
                ],
                max_tokens=10
            )
            
            if response.choices[0].message.content:
                print("✅ OpenAI API 正常")
                print(f"   回覆: {response.choices[0].message.content}")
                print(f"   Token 使用: {response.usage.total_tokens}")
            else:
                print("❌ OpenAI API 無回覆")
                
        except Exception as e:
            print(f"❌ OpenAI API 檢查失敗: {e}")
        
        print()
    
    async def check_google_sheets(self):
        """檢查 Google Sheets"""
        print("📋 Google Sheets 檢查")
        print("=" * 50)
        
        try:
            from src.clients.google.sheets_client import GoogleSheetsClient
            
            # 檢查憑證文件
            credentials_file = "./credentials/google-service-account.json"
            if os.path.exists(credentials_file):
                print("✅ Google Service Account 憑證文件存在")
            else:
                print("❌ Google Service Account 憑證文件不存在")
                print("   請下載憑證文件到: ./credentials/google-service-account.json")
                return
            
            # 測試連接
            sheets_client = GoogleSheetsClient(
                credentials_file=credentials_file,
                spreadsheet_id=self.google_sheets_id
            )
            
            # 檢查分頁是否存在
            try:
                sheet_data = sheets_client.read_sheet('貼文紀錄表', 'A1:Z1')
                if sheet_data and len(sheet_data) > 0:
                    headers = sheet_data[0]
                    print(f"✅ 貼文紀錄表 分頁存在，有 {len(headers)} 個欄位")
                    
                    # 檢查最後一行數據
                    last_row_data = sheets_client.read_sheet('貼文紀錄表', 'A:Z')
                    if last_row_data and len(last_row_data) > 1:
                        last_row = last_row_data[-1]
                        print(f"   最後一行: {last_row[0] if last_row else '無數據'}")
                    else:
                        print("   分頁為空")
                else:
                    print("❌ 貼文紀錄表 分頁為空或不存在")
                    
            except Exception as e:
                print(f"❌ 讀取貼文紀錄表失敗: {e}")
            
            # 檢查 KOL 角色紀錄表
            try:
                kol_data = sheets_client.read_sheet('KOL 角色紀錄表', 'A1:Z1')
                if kol_data and len(kol_data) > 0:
                    kol_headers = kol_data[0]
                    print(f"✅ KOL 角色紀錄表 分頁存在，有 {len(kol_headers)} 個欄位")
                else:
                    print("❌ KOL 角色紀錄表 分頁為空或不存在")
                    
            except Exception as e:
                print(f"❌ 讀取 KOL 角色紀錄表失敗: {e}")
                
        except Exception as e:
            print(f"❌ Google Sheets 檢查失敗: {e}")
        
        print()
    
    async def check_main_workflow(self):
        """檢查主工作流程"""
        print("⚙️ 主工作流程檢查")
        print("=" * 50)
        
        try:
            from src.core.main_workflow_engine import MainWorkflowEngine
            
            # 初始化工作流程引擎
            workflow_engine = MainWorkflowEngine()
            print("✅ 主工作流程引擎初始化成功")
            
            # 檢查配置
            config = workflow_engine.config
            print(f"✅ 配置載入成功")
            print(f"   Google Sheets ID: {config.google.spreadsheet_id}")
            print(f"   憑證文件: {config.google.credentials_file}")
            
            # 檢查 KOL 設定
            kol_settings = workflow_engine.config_manager.get_kol_personalization_settings()
            if kol_settings:
                print(f"✅ KOL 設定載入成功，共 {len(kol_settings)} 個 KOL")
                for kol_id, settings in list(kol_settings.items())[:3]:
                    print(f"   {kol_id}: {settings.get('persona', 'Unknown')}")
            else:
                print("❌ KOL 設定載入失敗")
                
        except Exception as e:
            print(f"❌ 主工作流程檢查失敗: {e}")
        
        print()
    
    async def test_after_hours_limit_up_workflow(self):
        """測試盤後漲停工作流程"""
        print("🚀 盤後漲停工作流程測試")
        print("=" * 50)
        
        try:
            from src.core.main_workflow_engine import MainWorkflowEngine, WorkflowConfig, WorkflowType
            
            # 初始化工作流程引擎
            workflow_engine = MainWorkflowEngine()
            
            # 創建測試配置
            config = WorkflowConfig(
                workflow_type=WorkflowType.AFTER_HOURS_LIMIT_UP,
                max_posts_per_topic=1,  # 只測試 1 篇
                enable_content_generation=True,
                enable_publishing=False,
                enable_learning=True,
                enable_quality_check=True,
                enable_sheets_recording=True,
                retry_on_failure=True,
                max_retries=3
            )
            
            print("✅ 開始執行盤後漲停工作流程測試...")
            
            # 執行工作流程
            result = await workflow_engine.execute_workflow(WorkflowType.AFTER_HOURS_LIMIT_UP, config)
            
            if result.success:
                print(f"✅ 工作流程執行成功")
                print(f"   生成貼文數: {result.total_posts_generated}")
                print(f"   執行時間: {result.execution_time:.2f} 秒")
                
                if result.errors:
                    print(f"   錯誤: {len(result.errors)} 個")
                    for error in result.errors[:3]:
                        print(f"     - {error}")
                        
                if result.warnings:
                    print(f"   警告: {len(result.warnings)} 個")
                    for warning in result.warnings[:3]:
                        print(f"     - {warning}")
            else:
                print(f"❌ 工作流程執行失敗")
                for error in result.errors:
                    print(f"   - {error}")
                    
        except Exception as e:
            print(f"❌ 盤後漲停工作流程測試失敗: {e}")
        
        print()
    
    async def run_complete_check(self):
        """執行完整檢查"""
        print("🔍 盤後漲停觸發器完整流程數據檢查")
        print("=" * 80)
        print(f"檢查時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # 1. API 金鑰檢查
        self._check_api_keys()
        
        # 2. FinLab API 檢查
        await self.check_finlab_api()
        
        # 3. Serper API 檢查
        await self.check_serper_api()
        
        # 4. OpenAI API 檢查
        await self.check_openai_api()
        
        # 5. Google Sheets 檢查
        await self.check_google_sheets()
        
        # 6. 主工作流程檢查
        await self.check_main_workflow()
        
        # 7. 盤後漲停工作流程測試
        await self.test_after_hours_limit_up_workflow()
        
        print("=" * 80)
        print("🎉 完整檢查完成！")
        print("📋 請根據上述檢查結果修復問題")

async def main():
    """主函數"""
    try:
        checker = DataCheckEngine()
        await checker.run_complete_check()
    except Exception as e:
        logger.error(f"數據檢查過程中發生錯誤: {e}")

if __name__ == "__main__":
    asyncio.run(main())
