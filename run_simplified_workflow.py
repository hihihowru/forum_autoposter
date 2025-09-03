#!/usr/bin/env python3
"""
AI 發文系統完整流程執行器 (簡化版)
整合熱門話題觸發器和漲停股觸發器
"""

import os
import sys
import asyncio
import openai
from openai import OpenAI
from datetime import datetime
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 設置 OpenAI API
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

class SimplifiedWorkflowRunner:
    def __init__(self):
        self.spreadsheet_id = os.getenv('GOOGLE_SHEETS_SPREADSHEET_ID')
        print(f"📊 使用 Google Sheets ID: {self.spreadsheet_id}")
        
    async def run_hot_topics_trigger(self):
        """執行熱門話題觸發器 (模擬)"""
        print("🔥 啟動熱門話題觸發器...")
        
        # 模擬熱門話題
        hot_topics = [
            {"id": "topic_001", "title": "台股高檔震盪，開高走平背後的真相？", "keywords": "台股,大盤,震盪"},
            {"id": "topic_002", "title": "AI概念股強勢，台積電領軍上攻", "keywords": "AI,台積電,科技股"},
            {"id": "topic_003", "title": "通膨數據出爐，央行政策走向引關注", "keywords": "通膨,央行,利率"}
        ]
        
        print(f"📊 獲取到 {len(hot_topics)} 個熱門話題")
        
        # 模擬 KOL
        kols = [
            {"serial": "200", "nickname": "川川哥", "persona": "籌碼派"},
            {"serial": "201", "nickname": "韭割哥", "persona": "情緒派"}
        ]
        
        for topic in hot_topics[:2]:  # 處理前2個話題
            print(f"📝 處理話題: {topic['title']}")
            
            for kol in kols:
                await self.generate_content(
                    topic=topic,
                    kol=kol,
                    trigger_type="hot_topics"
                )
                
    async def run_limit_up_stocks_trigger(self):
        """執行漲停股觸發器"""
        print("🚀 啟動漲停股觸發器...")
        
        # 模擬漲停股列表
        limit_up_stocks = [
            {"symbol": "6919", "name": "康霈生技", "reason": "減重藥題材發酵"},
            {"symbol": "2330", "name": "台積電", "reason": "AI需求強勁"},
            {"symbol": "2454", "name": "聯發科", "reason": "5G晶片出貨成長"}
        ]
        
        print(f"📈 獲取到 {len(limit_up_stocks)} 檔漲停股")
        
        # 模擬 KOL
        kols = [
            {"serial": "200", "nickname": "川川哥", "persona": "籌碼派"},
            {"serial": "201", "nickname": "韭割哥", "persona": "情緒派"}
        ]
        
        for stock in limit_up_stocks[:2]:  # 處理前2檔
            print(f"📊 處理股票: {stock['name']}({stock['symbol']})")
            
            for kol in kols:
                await self.generate_content(
                    stock=stock,
                    kol=kol,
                    trigger_type="limit_up_stocks"
                )
    
    async def generate_content(self, topic=None, stock=None, kol=None, trigger_type="unknown"):
        """生成內容"""
        try:
            print(f"🎯 開始為 KOL {kol['nickname']} 生成內容...")
            
            # 準備生成參數
            if topic:
                content_type = "熱門話題分析"
                subject = f"{topic['title']}"
                keywords = topic['keywords']
            elif stock:
                content_type = "漲停股分析"
                subject = f"{stock['name']}({stock['symbol']}) - {stock['reason']}"
                keywords = f"{stock['name']},{stock['symbol']}"
            else:
                return
                
            # 生成個人化提示詞
            prompt = self.build_personalized_prompt(
                kol=kol,
                subject=subject,
                content_type=content_type,
                keywords=keywords,
                trigger_type=trigger_type
            )
            
            # 調用 OpenAI API
            response = await self.call_openai_api(prompt)
            
            if response:
                print(f"✅ KOL {kol['nickname']} 內容生成成功")
                
                # 模擬記錄到 Google Sheets
                await self.simulate_record_to_sheets(
                    kol=kol,
                    content=response,
                    trigger_type=trigger_type,
                    topic=topic,
                    stock=stock
                )
            else:
                print(f"❌ KOL {kol['nickname']} 內容生成失敗")
                
        except Exception as e:
            print(f"❌ 內容生成錯誤: {e}")
    
    def build_personalized_prompt(self, kol, subject, content_type, keywords, trigger_type):
        """建立個人化提示詞"""
        
        # 根據 KOL 人設調整語氣
        if kol['persona'] == '籌碼派':
            tone_guidance = """
            語氣要求：
            - 專注於籌碼面分析，強調資金流向和大戶動向
            - 使用專業的籌碼分析術語
            - 語氣冷靜理性，注重數據支撐
            - 避免過度情緒化表達
            """
        elif kol['persona'] == '情緒派':
            tone_guidance = """
            語氣要求：
            - 注重市場情緒和投資人心理變化
            - 使用生動的比喻和故事性表達
            - 語氣活潑，善於營造氛圍
            - 可以適當使用感嘆號和問句
            """
        else:
            tone_guidance = "語氣要求：專業中性的分析語氣"
        
        prompt = f"""
你是一個專業的台股分析師，代號「{kol['nickname']}」，人設是「{kol['persona']}」。

{tone_guidance}

請針對以下主題生成一篇台股分析貼文：

主題：{subject}
內容類型：{content_type}
關鍵字：{keywords}
觸發類型：{trigger_type}

要求：
1. 直接生成標題和內容，不要加任何前綴如"標題："或"內容："
2. 標題要吸引人，符合{kol['persona']}的風格
3. 內容要專業且個人化，體現{kol['persona']}的分析特色
4. 內容長度控制在300-500字
5. 結尾要有互動性，鼓勵讀者留言討論

請開始生成：
"""
        return prompt
    
    async def call_openai_api(self, prompt):
        """調用 OpenAI API"""
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "你是一個專業的台股分析師，擅長生成個人化的投資分析內容。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.8
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"❌ OpenAI API 調用失敗: {e}")
            return None
    
    async def simulate_record_to_sheets(self, kol, content, trigger_type, topic=None, stock=None):
        """模擬記錄到 Google Sheets"""
        try:
            # 模擬記錄數據
            record_data = {
                'post_id': f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{kol['serial']}",
                'kol_serial': kol['serial'],
                'kol_nickname': kol['nickname'],
                'persona': kol['persona'],
                'content_type': '熱門話題分析' if topic else '漲停股分析',
                'topic_title': topic['title'] if topic else f"{stock['name']}({stock['symbol']})",
                'content': content,
                'status': '已生成',
                'trigger_type': trigger_type,
                'content_generation_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'kol_settings_version': 'v3.0_simplified_workflow'
            }
            
            print(f"📝 模擬記錄到 Google Sheets: {record_data['post_id']}")
            title_line = content.split('\n')[0] if content else 'N/A'
            print(f"   標題: {title_line}")
            print(f"   KOL: {kol['nickname']} ({kol['persona']})")
            print(f"   觸發器: {trigger_type}")
            print("-" * 40)
            
        except Exception as e:
            print(f"❌ 模擬記錄失敗: {e}")
    
    async def run_complete_workflow(self):
        """執行完整工作流程"""
        print("🚀 開始執行 AI 發文系統完整流程 (簡化版)")
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
        print("📊 流程總結:")
        print("   - 熱門話題觸發器: 2個話題 × 2個KOL = 4篇內容")
        print("   - 漲停股觸發器: 2檔股票 × 2個KOL = 4篇內容")
        print("   - 總計: 8篇個人化內容已生成")

async def main():
    """主函數"""
    runner = SimplifiedWorkflowRunner()
    await runner.run_complete_workflow()

if __name__ == "__main__":
    asyncio.run(main())
