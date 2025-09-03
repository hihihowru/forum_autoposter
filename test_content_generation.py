#!/usr/bin/env python3
"""
測試內容生成，使用新的0-10評分系統
"""

import os
import sys
import asyncio
from datetime import datetime

# 添加項目路徑
sys.path.append('.')

from src.services.assign.assignment_service import AssignmentService, TopicData
from src.services.content.data_driven_content_generator import DataDrivenContentGenerator
from src.services.content.enhanced_prompt_generator import EnhancedPromptGenerator
from src.services.content.content_quality_checker import ContentQualityChecker
from src.services.content.content_regenerator import ContentRegenerator
from src.services.sheets.enhanced_sheets_recorder import EnhancedSheetsRecorder
from src.clients.google.sheets_client import GoogleSheetsClient

# 模擬股票數據
class MockStockMarketData:
    def __init__(self, stock_id, stock_name, close, daily_change_pct, technical_summary):
        self.stock_id = stock_id
        self.stock_name = stock_name
        self.close = close
        self.daily_change_pct = daily_change_pct
        self.technical_summary = technical_summary
        self.date = datetime.now().strftime("%Y-%m-%d")

async def test_content_generation():
    """測試內容生成流程"""
    
    print("🧪 測試新的0-10評分系統內容生成")
    print("=" * 60)
    
    # 創建服務
    sheets_client = GoogleSheetsClient(
        credentials_file='./credentials/google-service-account.json',
        spreadsheet_id='148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LikN2s'
    )
    
    assignment_service = AssignmentService(sheets_client)
    assignment_service.load_kol_profiles()
    
    # 創建內容生成相關服務
    prompt_generator = EnhancedPromptGenerator()
    quality_checker = ContentQualityChecker()
    content_regenerator = ContentRegenerator(prompt_generator, quality_checker)
    content_generator = DataDrivenContentGenerator()
    sheets_recorder = EnhancedSheetsRecorder(sheets_client)
    
    print(f"✅ 載入了 {len(assignment_service._kol_profiles)} 個 KOL")
    
    # 創建測試話題
    test_topics = [
        TopicData(
            topic_id='cbb97e62-3fe3-4304-803e-98d7e447d852',
            title='台股開盤指數上漲拉回，內外資分歧下大盤...',
            input_index=0,
            persona_tags=['籌碼派', '情緒派'],
            industry_tags=['大盤'],
            event_tags=['開盤'],
            stocks=[{'name_zh': '台積電', 'stock_id': '2330'}],
            primary_stock={'name_zh': '台積電', 'stock_id': '2330'},
            stock_tags=['2330']
        ),
        TopicData(
            topic_id='4d3eab24-dc2d-4051-9656-15dc8cb90eb9',
            title='大盤重返2萬4！台股9月走勢將...',
            input_index=1,
            persona_tags=['總經派', '情緒派'],
            industry_tags=['大盤'],
            event_tags=['趨勢分析'],
            stocks=[{'name_zh': '台積電', 'stock_id': '2330'}],
            primary_stock={'name_zh': '台積電', 'stock_id': '2330'},
            stock_tags=['2330']
        )
    ]
    
    # 模擬股票數據（使用新的0-10評分）
    stock_data_map = {
        "2330": MockStockMarketData(
            "2330", "台積電", 1160.00, -0.6,
            "台積電: 技術面呈現震盪整理格局。MACD柱狀圖轉弱，季線強勢突破(4.2%)，中期KD死亡交叉，短期波動率異常升高。有效指標數: 7。評分: 4.7/10 (信心度: 31.9%)"
        )
    }
    
    # 模擬市場上下文
    class MockMarketContext:
        def __init__(self):
            self.news_highlights = "台股開盤指數上漲拉回，內外資分歧下大盤"
            self.market_trend = "震盪"
    
    market_context = MockMarketContext()
    
    # 為每個話題生成內容
    for topic in test_topics:
        print(f"\n📋 處理話題: {topic.title}")
        print("-" * 40)
        
        # 分派KOL
        assignments = assignment_service.assign_topics([topic], max_assignments_per_topic=2)
        print(f"👥 分派給 {len(assignments)} 個 KOL")
        
        if not assignments:
            print("❌ 沒有KOL被分派")
            continue
        
        # 為每個分派的KOL生成內容
        for assignment in assignments:
            kol = next((k for k in assignment_service._kol_profiles if k.serial == assignment.kol_serial), None)
            if not kol:
                continue
                
            print(f"\n🎭 為 {kol.nickname} ({kol.persona}) 生成內容")
            
            # 準備股票摘要
            stock_summary = content_generator._prepare_stock_summary_for_kol(
                [{'stock_id': '2330', 'stock_name': '台積電', 'analysis_angle': '技術面分析'}],
                stock_data_map,
                kol.persona
            )
            
            print(f"📊 股票摘要: {stock_summary['stock_summary'][:100]}...")
            if stock_summary.get('technical_explanation'):
                print(f"📝 技術解釋: {stock_summary['technical_explanation'][:100]}...")
            
            # 生成增強版Prompt
            enhanced_prompt = prompt_generator.generate_enhanced_prompt(
                kol_serial=str(kol.serial),
                kol_nickname=kol.nickname,
                persona=kol.persona,
                topic_title=topic.title,
                stock_data=stock_summary,
                market_context=market_context.news_highlights
            )
            
            print(f"🎯 生成Prompt成功，系統提示詞長度: {len(enhanced_prompt.get('system_prompt', ''))}")
            
            # 模擬內容生成（因為沒有OpenAI API key）
            mock_content = {
                'title': f"{kol.nickname}的觀點：{topic.title}",
                'content': f"""
大家好！我是{kol.nickname}，今天來聊聊{topic.title}。

根據最新的技術分析，台積電(2330)目前評分為4.7/10，處於震盪整理階段。

{stock_summary.get('technical_explanation', '技術分析數據顯示市場方向不明')}

我的看法是，在內外資分歧的情況下，建議投資人保持觀望，等待更明確的技術信號。

你們怎麼看呢？歡迎在下方留言分享你的觀點！
                """.strip(),
                'raw_response': "模擬生成的內容"
            }
            
            print(f"✅ 內容生成完成")
            print(f"📝 標題: {mock_content['title']}")
            print(f"📄 內容長度: {len(mock_content['content'])} 字")
            
            # 記錄到Google Sheets
            try:
                from src.services.content.models import GeneratedPost
                
                # 創建模擬的GeneratedPost
                post = GeneratedPost(
                    post_id=f"{topic.topic_id}-{kol.serial}",
                    kol_serial=str(kol.serial),
                    kol_nickname=kol.nickname,
                    persona=kol.persona,
                    title=mock_content['title'],
                    content=mock_content['content'],
                    topic_title=topic.title,
                    topic_id=topic.topic_id,
                    generation_params={'model': 'gpt-4o-mini', 'temperature': 0.7},
                    created_at=datetime.now()
                )
                
                # 記錄到Google Sheets
                sheets_recorder.record_enhanced_post(post, stock_summary)
                print(f"✅ 成功記錄到Google Sheets")
                
            except Exception as e:
                print(f"❌ 記錄到Google Sheets失敗: {e}")
    
    print(f"\n🎉 內容生成測試完成！")
    print(f"📋 請檢查Google Sheets的貼文記錄表，應該有新的貼文記錄")

if __name__ == "__main__":
    asyncio.run(test_content_generation())



