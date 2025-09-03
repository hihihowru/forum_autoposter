#!/usr/bin/env python3
"""
測試話題分類系統
"""

import sys
import os
sys.path.append('./src')

from services.classification.topic_classifier import create_topic_classifier

def test_topic_classification():
    """測試話題分類功能"""
    print("=== 測試話題分類系統 ===")
    print()
    
    try:
        # 創建分類器
        classifier = create_topic_classifier()
        print("✅ 話題分類器初始化成功")
        print()
        
        # 測試話題
        test_topics = [
            {
                "id": "test_001",
                "title": "台積電法說會亮眼，AI需求強勁帶動營收成長",
                "content": "台積電最新法說會顯示AI需求持續強勁，營收展望樂觀。公司表示先進製程產能利用率維持高檔，3奈米製程需求強勁。"
            },
            {
                "id": "test_002", 
                "title": "聯發科5G晶片市占率提升，技術分析顯示突破關鍵阻力",
                "content": "聯發科在5G晶片市場表現亮眼，市占率持續提升。技術面來看，股價突破關鍵阻力位，RSI指標顯示超買，但MACD仍維持多頭排列。"
            },
            {
                "id": "test_003",
                "title": "央行升息政策影響金融股表現，外資大舉買超",
                "content": "央行宣布升息一碼，對金融股產生正面影響。外資昨日大舉買超金融股，投信也跟進加碼。市場預期升息將提升銀行淨利差。"
            },
            {
                "id": "test_004",
                "title": "鴻海電動車布局加速，與多家車廠簽署合作協議",
                "content": "鴻海在電動車領域布局加速，與多家車廠簽署合作協議。公司表示將投入更多資源發展電動車業務，預期未來幾年將成為重要成長動能。"
            }
        ]
        
        # 分類每個話題
        for i, topic in enumerate(test_topics, 1):
            print(f"--- 測試話題 {i} ---")
            print(f"標題: {topic['title']}")
            print()
            
            # 進行分類
            classification = classifier.classify_topic(
                topic_id=topic['id'],
                title=topic['title'],
                content=topic['content']
            )
            
            # 顯示結果
            print("分類結果:")
            print(f"  人設標籤: {classification.persona_tags}")
            print(f"  產業標籤: {classification.industry_tags}")
            print(f"  事件標籤: {classification.event_tags}")
            print(f"  股票標籤: {classification.stock_tags}")
            print(f"  信心度: {classification.confidence_score:.2f}")
            print()
        
        print("✅ 話題分類測試完成")
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_topic_classification()
