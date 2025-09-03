#!/usr/bin/env python3
"""
測試話題分派調試
"""

import os
import sys
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.clients.google.sheets_client import GoogleSheetsClient
from src.services.assign.assignment_service import AssignmentService, TopicData
from src.services.classification.topic_classifier import TopicClassifier

def test_assignment_debug():
    """測試話題分派調試"""
    
    print("=== 測試話題分派調試 ===\n")
    
    # 初始化服務
    sheets_client = GoogleSheetsClient(
        credentials_file=os.getenv('GOOGLE_CREDENTIALS_FILE'),
        spreadsheet_id=os.getenv('GOOGLE_SHEETS_ID')
    )
    
    assignment_service = AssignmentService(sheets_client)
    topic_classifier = TopicClassifier()
    
    try:
        # 載入 KOL 配置
        print("載入 KOL 配置...")
        assignment_service.load_kol_profiles()
        print(f"載入了 {len(assignment_service._kol_profiles)} 個 KOL")
        
        # 創建測試話題
        test_topic = TopicData(
            topic_id="test-topic-001",
            title="台股開紅漲逾155點! 台積鏈/無人機齊揚",
            input_index=0,
            persona_tags=['新聞派'],
            industry_tags=['半導體', '科技'],
            event_tags=[],
            stock_tags=[]
        )
        
        print(f"\n測試話題: {test_topic.title}")
        print(f"人設標籤: {test_topic.persona_tags}")
        print(f"產業標籤: {test_topic.industry_tags}")
        
        # 計算每個 KOL 的匹配分數
        print(f"\n計算匹配分數:")
        kol_scores = []
        for kol in assignment_service._kol_profiles:
            if not kol.enabled:
                continue
            
            score = assignment_service.calculate_match_score(test_topic, kol)
            kol_scores.append({
                'kol': kol,
                'score': score
            })
            
            print(f"  {kol.serial}: {kol.nickname} ({kol.persona}) - 分數: {score}")
            print(f"    偏好: {kol.topic_preferences}")
            print(f"    禁講: {kol.forbidden_categories}")
        
        # 排序並顯示結果
        kol_scores.sort(key=lambda x: x['score'], reverse=True)
        print(f"\n排序後的匹配分數:")
        for item in kol_scores:
            kol = item['kol']
            score = item['score']
            print(f"  {score:.2f} - {kol.serial}: {kol.nickname} ({kol.persona})")
        
        # 測試分派
        print(f"\n測試分派 (max_assignments_per_topic=2):")
        assignments = assignment_service.assign_topics([test_topic], max_assignments_per_topic=2)
        print(f"分派結果: {len(assignments)} 個任務")
        
        for assignment in assignments:
            print(f"  - {assignment.task_id}: KOL {assignment.kol_serial}")
        
        print("\n✅ 話題分派調試完成！")
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_assignment_debug()
