#!/usr/bin/env python3
"""
測試話題處理流程
包括話題分類、KOL分配、內容生成和更新貼文記錄表
"""

import sys
import os
sys.path.append('./src')

from services.assign.topic_processor import create_topic_processor
from clients.google.sheets_client import GoogleSheetsClient

def test_topic_processing():
    """測試話題處理流程"""
    print("=== 測試話題處理流程 ===")
    print()
    
    try:
        # 初始化服務
        sheets_client = GoogleSheetsClient(
            credentials_file='credentials/google-service-account.json',
            spreadsheet_id='148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LikN2s'
        )
        
        processor = create_topic_processor(sheets_client)
        print("✅ 話題處理器初始化成功")
        print()
        
        # 測試話題
        test_topics = [
            {
                "id": "process_test_001",
                "title": "台積電法說會亮眼，AI需求強勁帶動營收成長",
                "content": "台積電最新法說會顯示AI需求持續強勁，營收展望樂觀。公司表示先進製程產能利用率維持高檔，3奈米製程需求強勁。"
            },
            {
                "id": "process_test_002", 
                "title": "聯發科5G晶片市占率提升，技術分析顯示突破關鍵阻力",
                "content": "聯發科在5G晶片市場表現亮眼，市占率持續提升。技術面來看，股價突破關鍵阻力位，RSI指標顯示超買，但MACD仍維持多頭排列。"
            }
        ]
        
        print(f"準備處理 {len(test_topics)} 個話題...")
        print()
        
        # 處理話題
        processed_topics = processor.process_topics(test_topics)
        
        print("=== 處理結果摘要 ===")
        for i, topic in enumerate(processed_topics, 1):
            print(f"話題 {i}: {topic.title}")
            print(f"  分配了 {len(topic.assignments)} 個 KOL")
            print(f"  生成了 {len(topic.generated_content)} 個內容")
            
            for assignment in topic.assignments:
                # 根據 kol_serial 找到對應的 KOL 物件
                kol = next((k for k in processor.assignment_service._kol_profiles if k.serial == assignment.kol_serial), None)
                if kol:
                    has_content = assignment.kol_serial in topic.generated_content
                    print(f"    - {kol.nickname} ({kol.persona}): {'✅' if has_content else '❌'}")
                else:
                    print(f"    - KOL serial {assignment.kol_serial}: ❌ (找不到KOL)")
            print()
        
        print("✅ 話題處理測試完成")
        print()
        
        # 檢查貼文記錄表
        print("=== 檢查貼文記錄表 ===")
        post_data = sheets_client.read_sheet('貼文記錄表', 'A:Q')
        headers = post_data[0]
        rows = post_data[1:]
        
        print(f"貼文記錄表現在有 {len(rows)} 筆記錄")
        
        if rows:
            print("最新記錄:")
            for i, row in enumerate(rows[-3:], 1):  # 顯示最後3筆
                print(f"記錄 {i}:")
                print(f"  貼文ID: {row[0] if len(row) > 0 else 'N/A'}")
                print(f"  KOL: {row[2] if len(row) > 2 else 'N/A'} ({row[1] if len(row) > 1 else 'N/A'})")
                print(f"  話題: {row[8] if len(row) > 8 else 'N/A'}")
                print(f"  狀態: {row[11] if len(row) > 11 else 'N/A'}")
                print(f"  內容長度: {len(row[10]) if len(row) > 10 and row[10] else 0} 字")
                print()
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_topic_processing()
