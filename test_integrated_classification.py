#!/usr/bin/env python3
"""
測試整合後的話題分類和派發系統
"""

import sys
import os
sys.path.append('./src')

from services.assign.assignment_service import AssignmentService, TopicData
from clients.google.sheets_client import GoogleSheetsClient

def test_integrated_system():
    """測試整合後的分類和派發系統"""
    print("=== 測試整合後的話題分類和派發系統 ===")
    print()
    
    try:
        # 初始化服務
        sheets_client = GoogleSheetsClient(
            credentials_file='credentials/google-service-account.json',
            spreadsheet_id='148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LikN2s'
        )
        
        assignment_service = AssignmentService(sheets_client)
        print("✅ 派發服務初始化成功")
        print()
        
        # 測試話題
        test_topics = [
            {
                "id": "integrated_test_001",
                "title": "台積電法說會亮眼，AI需求強勁帶動營收成長",
                "content": "台積電最新法說會顯示AI需求持續強勁，營收展望樂觀。公司表示先進製程產能利用率維持高檔，3奈米製程需求強勁。"
            },
            {
                "id": "integrated_test_002", 
                "title": "聯發科5G晶片市占率提升，技術分析顯示突破關鍵阻力",
                "content": "聯發科在5G晶片市場表現亮眼，市占率持續提升。技術面來看，股價突破關鍵阻力位，RSI指標顯示超買，但MACD仍維持多頭排列。"
            }
        ]
        
        # 處理每個話題
        for i, topic_data in enumerate(test_topics, 1):
            print(f"--- 處理話題 {i} ---")
            print(f"標題: {topic_data['title']}")
            print()
            
            # 步驟1: 話題分類
            print("步驟1: 話題分類")
            classification = assignment_service.classify_topic(
                topic_id=topic_data['id'],
                title=topic_data['title'],
                content=topic_data['content']
            )
            
            print(f"  人設標籤: {classification.persona_tags}")
            print(f"  產業標籤: {classification.industry_tags}")
            print(f"  事件標籤: {classification.event_tags}")
            print(f"  股票標籤: {classification.stock_tags}")
            print(f"  信心度: {classification.confidence_score:.2f}")
            print()
            
            # 步驟2: 創建 TopicData 物件
            print("步驟2: 創建 TopicData 物件")
            topic = TopicData(
                topic_id=topic_data['id'],
                title=topic_data['title'],
                input_index=i,
                persona_tags=classification.persona_tags,
                industry_tags=classification.industry_tags,
                event_tags=classification.event_tags,
                stock_tags=classification.stock_tags,
                classification=classification
            )
            print(f"  TopicData 創建完成")
            print()
            
            # 步驟3: 載入 KOL 配置
            print("步驟3: 載入 KOL 配置")
            assignment_service.load_kol_profiles()
            print(f"  載入了 {len(assignment_service._kol_profiles)} 個 KOL")
            print()
            
            # 步驟4: 計算匹配分數
            print("步驟4: 計算匹配分數")
            kol_scores = []
            for kol in assignment_service._kol_profiles[:3]:  # 只測試前3個KOL
                if kol.enabled:
                    score = assignment_service.calculate_match_score(topic, kol)
                    kol_scores.append({
                        'kol': kol,
                        'score': score
                    })
                    print(f"  {kol.nickname} ({kol.persona}): {score:.2f}")
            
            # 排序並顯示結果
            kol_scores.sort(key=lambda x: x['score'], reverse=True)
            print()
            print("匹配結果排序:")
            for item in kol_scores:
                print(f"  {item['kol'].nickname}: {item['score']:.2f}")
            
            print()
            print("=" * 50)
            print()
        
        print("✅ 整合測試完成")
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_integrated_system()
