#!/usr/bin/env python3
"""
AI 發文系統完整流程執行器
整合熱門話題觸發器和漲停股觸發器
"""

import os
import sys
import asyncio
from datetime import datetime
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 添加 src 目錄到 Python 路徑
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from services.content.personalized_prompt_generator import PersonalizedPromptGenerator
from services.sheets.enhanced_sheets_recorder import EnhancedSheetsRecorder
from clients.cmoney.cmoney_client import CMoneyClient
from clients.google.sheets_client import GoogleSheetsClient

class CompleteWorkflowRunner:
    def __init__(self):
        self.sheets_client = GoogleSheetsClient(
            credentials_file='credentials/google-service-account.json',
            spreadsheet_id=os.getenv('GOOGLE_SHEETS_SPREADSHEET_ID')
        )
        self.cmoney_client = CMoneyClient()
        self.prompt_generator = PersonalizedPromptGenerator()
        self.sheets_recorder = EnhancedSheetsRecorder()
        
    async def run_hot_topics_trigger(self):
        """執行熱門話題觸發器"""
        print("🔥 啟動熱門話題觸發器...")
        
        try:
            # 獲取熱門話題
            trending_topics = await self.cmoney_client.get_trending_topics()
            print(f"📊 獲取到 {len(trending_topics)} 個熱門話題")
            
            # 為每個話題生成內容
            for topic in trending_topics[:3]:  # 限制前3個話題
                print(f"📝 處理話題: {topic.title}")
                
                # 獲取可用 KOL
                kol_credentials = self.get_active_kols()
                
                for kol in kol_credentials[:2]:  # 每個話題分配2個KOL
                    await self.generate_and_publish_content(
                        topic=topic,
                        kol=kol,
                        trigger_type="hot_topics"
                    )
                    
        except Exception as e:
            print(f"❌ 熱門話題觸發器錯誤: {e}")
            
    async def run_limit_up_stocks_trigger(self):
        """執行漲停股觸發器"""
        print("🚀 啟動漲停股觸發器...")
        
        try:
            # 模擬獲取漲停股列表 (未來會從 API 獲取)
            limit_up_stocks = [
                {"symbol": "6919", "name": "康霈生技", "reason": "減重藥題材發酵"},
                {"symbol": "2330", "name": "台積電", "reason": "AI需求強勁"},
                {"symbol": "2454", "name": "聯發科", "reason": "5G晶片出貨成長"}
            ]
            
            print(f"📈 獲取到 {len(limit_up_stocks)} 檔漲停股")
            
            # 為每檔股票生成內容
            for stock in limit_up_stocks[:2]:  # 限制前2檔
                print(f"📊 處理股票: {stock['name']}({stock['symbol']})")
                
                # 獲取可用 KOL
                kol_credentials = self.get_active_kols()
                
                for kol in kol_credentials[:2]:  # 每檔股票分配2個KOL
                    await self.generate_and_publish_content(
                        stock=stock,
                        kol=kol,
                        trigger_type="limit_up_stocks"
                    )
                    
        except Exception as e:
            print(f"❌ 漲停股觸發器錯誤: {e}")
    
    def get_active_kols(self):
        """獲取活躍的 KOL 列表"""
        try:
            # 從 Google Sheets 讀取 KOL 資料
            kol_data = self.sheets_client.read_sheet("同學會帳號管理")
            
            active_kols = []
            for row in kol_data[1:]:  # 跳過標題行
                if len(row) >= 10 and row[9] == 'active':  # 狀態欄位
                    kol = {
                        'serial': row[0],
                        'nickname': row[1],
                        'member_id': row[2],
                        'persona': row[3],
                        'username': row[4],
                        'password': row[5]
                    }
                    active_kols.append(kol)
                    
            print(f"👥 找到 {len(active_kols)} 個活躍 KOL")
            return active_kols
            
        except Exception as e:
            print(f"❌ 獲取 KOL 資料錯誤: {e}")
            # 返回預設 KOL
            return [
                {
                    'serial': '200',
                    'nickname': '川川哥',
                    'member_id': '200',
                    'persona': '籌碼派',
                    'username': 'test_user_1',
                    'password': 'test_pass_1'
                },
                {
                    'serial': '201', 
                    'nickname': '韭割哥',
                    'member_id': '201',
                    'persona': '情緒派',
                    'username': 'test_user_2',
                    'password': 'test_pass_2'
                }
            ]
    
    async def generate_and_publish_content(self, topic=None, stock=None, kol=None, trigger_type="unknown"):
        """生成並發布內容"""
        try:
            print(f"🎯 開始為 KOL {kol['nickname']} 生成內容...")
            
            # 準備生成參數
            if topic:
                content_type = "熱門話題分析"
                subject = f"{topic.title}"
                keywords = topic.keywords
            elif stock:
                content_type = "漲停股分析"
                subject = f"{stock['name']}({stock['symbol']}) - {stock['reason']}"
                keywords = f"{stock['name']},{stock['symbol']}"
            else:
                return
                
            # 生成個人化內容
            generated_content = await self.prompt_generator.generate_personalized_content(
                kol_serial=kol['serial'],
                topic_title=subject,
                content_type=content_type,
                keywords=keywords,
                trigger_type=trigger_type
            )
            
            if not generated_content:
                print(f"❌ KOL {kol['nickname']} 內容生成失敗")
                return
                
            print(f"✅ KOL {kol['nickname']} 內容生成成功")
            
            # 記錄到 Google Sheets
            await self.record_to_sheets(
                kol=kol,
                content=generated_content,
                trigger_type=trigger_type,
                topic=topic,
                stock=stock
            )
            
            # 發布到平台 (可選)
            # await self.publish_to_platform(kol, generated_content)
            
        except Exception as e:
            print(f"❌ 內容生成與發布錯誤: {e}")
    
    async def record_to_sheets(self, kol, content, trigger_type, topic=None, stock=None):
        """記錄到 Google Sheets"""
        try:
            # 準備記錄資料
            record_data = {
                'post_id': f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{kol['serial']}",
                'kol_serial': kol['serial'],
                'kol_nickname': kol['nickname'],
                'kol_id': kol['member_id'],
                'persona': kol['persona'],
                'content_type': content.get('content_type', ''),
                'topic_id': topic.id if topic else '',
                'topic_title': topic.title if topic else f"{stock['name']}({stock['symbol']})" if stock else '',
                'content': content.get('content', ''),
                'status': '已生成',
                'trigger_type': trigger_type,
                'generated_title': content.get('title', ''),
                'data_sources': content.get('data_sources', ''),
                'agent_decision_record': content.get('decision_record', ''),
                'content_generation_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'kol_settings_version': 'v3.0_complete_workflow'
            }
            
            # 寫入 Google Sheets
            await self.sheets_recorder.record_enhanced_post(record_data)
            print(f"📝 已記錄到 Google Sheets: {record_data['post_id']}")
            
        except Exception as e:
            print(f"❌ 記錄到 Google Sheets 錯誤: {e}")
    
    async def run_complete_workflow(self):
        """執行完整工作流程"""
        print("🚀 開始執行 AI 發文系統完整流程")
        print("=" * 50)
        
        start_time = datetime.now()
        
        # 1. 執行熱門話題觸發器
        await self.run_hot_topics_trigger()
        print("-" * 30)
        
        # 2. 執行漲停股觸發器
        await self.run_limit_up_stocks_trigger()
        print("-" * 30)
        
        # 3. 流程完成
        end_time = datetime.now()
        duration = end_time - start_time
        
        print("✅ 完整流程執行完成!")
        print(f"⏱️  總執行時間: {duration}")
        print("=" * 50)

async def main():
    """主函數"""
    runner = CompleteWorkflowRunner()
    await runner.run_complete_workflow()

if __name__ == "__main__":
    asyncio.run(main())

