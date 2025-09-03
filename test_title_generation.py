#!/usr/bin/env python3
"""
測試標題生成改進效果
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.content.content_generator import ContentGenerator, ContentRequest
from src.clients.google.sheets_client import GoogleSheetsClient

async def test_title_generation():
    """測試標題生成"""
    
    print("=== 測試標題生成改進效果 ===\n")
    
    # 初始化服務
    sheets_client = GoogleSheetsClient(
        credentials_file=os.getenv('GOOGLE_CREDENTIALS_FILE'),
        spreadsheet_id=os.getenv('GOOGLE_SHEETS_ID')
    )
    
    content_generator = ContentGenerator()
    
    # 測試話題
    test_topics = [
        {
            "title": "台積電法說會亮眼，AI需求強勁帶動營收成長",
            "keywords": "台積電,TSMC,法說會,AI,營收成長,半導體"
        },
        {
            "title": "聯發科5G晶片市占率提升，技術分析顯示突破關鍵阻力",
            "keywords": "聯發科,MTK,5G,晶片,技術分析,突破"
        }
    ]
    
    # 測試 KOL
    test_kols = [
        {"nickname": "川川哥", "persona": "技術派", "content_type": "technical,chart", "target_audience": "active_traders"},
        {"nickname": "韭割哥", "persona": "總經派", "content_type": "macro,policy", "target_audience": "long_term_investors"},
        {"nickname": "梅川褲子", "persona": "新聞派", "content_type": "news,trending", "target_audience": "active_traders"}
    ]
    
    for topic in test_topics:
        print(f"話題：{topic['title']}")
        print(f"關鍵詞：{topic['keywords']}\n")
        
        for kol in test_kols:
            # 創建內容請求
            request = ContentRequest(
                kol_nickname=kol['nickname'],
                kol_persona=kol['persona'],
                content_type=kol['content_type'],
                target_audience=kol['target_audience'],
                topic_title=topic['title'],
                topic_keywords=topic['keywords']
            )
            
            # 生成標題
            title = content_generator.generate_title(request)
            title_length = len(title)
            
            print(f"  {kol['nickname']} ({kol['persona']}): {title} ({title_length}字)")
        
        print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    asyncio.run(test_title_generation())
