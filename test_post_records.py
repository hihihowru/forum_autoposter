#!/usr/bin/env python3
"""
測試發文記錄功能
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.clients.cmoney.cmoney_client import CMoneyClient, LoginCredentials
from src.clients.google.sheets_client import GoogleSheetsClient
from src.services.assign.assignment_service import AssignmentService, TopicData
from src.services.classification.topic_classifier import TopicClassifier
from src.services.content.content_generator import ContentGenerator, ContentRequest

async def test_post_records():
    """測試發文記錄功能"""
    
    print("=== 測試發文記錄功能 ===\n")
    
    # 初始化服務
    sheets_client = GoogleSheetsClient(
        credentials_file=os.getenv('GOOGLE_CREDENTIALS_FILE'),
        spreadsheet_id=os.getenv('GOOGLE_SHEETS_ID')
    )
    
    cmoney_client = CMoneyClient()
    assignment_service = AssignmentService(sheets_client)
    topic_classifier = TopicClassifier()
    content_generator = ContentGenerator()
    
    try:
        # 步驟1: 獲取一個熱門話題
        print("步驟1: 獲取熱門話題...")
        credentials = LoginCredentials(
            email='forum_200@cmoney.com.tw',
            password='N9t1kY3x'
        )
        
        token = await cmoney_client.login(credentials)
        topics = await cmoney_client.get_trending_topics(token.token)
        
        if not topics:
            print("❌ 沒有獲取到熱門話題")
            return
        
        topic = topics[0]
        print(f"✅ 獲取到話題: {topic.title}")
        
        # 步驟2: 話題分類
        print("\n步驟2: 話題分類...")
        classification = topic_classifier.classify_topic(topic.id, topic.title, topic.name)
        print(f"✅ 分類結果: {classification.persona_tags}, {classification.industry_tags}")
        
        # 步驟3: KOL 分派
        print("\n步驟3: KOL 分派...")
        assignment_service.load_kol_profiles()
        
        topic_data = TopicData(
            topic_id=topic.id,
            title=topic.title,
            input_index=0,
            persona_tags=classification.persona_tags,
            industry_tags=classification.industry_tags,
            event_tags=classification.event_tags,
            stock_tags=classification.stock_tags,
            classification=classification
        )
        
        assignments = assignment_service.assign_topics([topic_data], max_assignments_per_topic=2)
        print(f"✅ 分派給 {len(assignments)} 個 KOL")
        
        # 步驟4: 生成內容並準備發文記錄
        print("\n步驟4: 生成內容並準備發文記錄...")
        post_records = []
        
        for assignment in assignments:
            # 找到對應的 KOL
            kol = next((k for k in assignment_service._kol_profiles if k.serial == assignment.kol_serial), None)
            if not kol:
                continue
            
            print(f"處理 KOL: {kol.nickname} (Serial: {assignment.kol_serial})")
            
            # 生成內容
            content_request = ContentRequest(
                topic_title=topic.title,
                topic_keywords=", ".join(classification.persona_tags + classification.industry_tags + classification.event_tags),
                kol_persona=kol.persona,
                kol_nickname=kol.nickname,
                content_type="investment",
                target_audience="active_traders"
            )
            
            generated = content_generator.generate_complete_content(content_request)
            
            if not generated.success:
                print(f"❌ 內容生成失敗: {generated.error_message}")
                continue
            
            # 生成 post ID
            post_id = f"{topic.id}-{assignment.kol_serial}"
            
            # 準備發文記錄
            record = [
                post_id,  # 貼文ID
                assignment.kol_serial,  # KOL Serial
                kol.nickname,  # KOL 暱稱
                kol.member_id,  # KOL ID
                kol.persona,  # Persona
                "investment",  # Content Type
                1,  # 已派發TopicIndex
                topic.id,  # 已派發TopicID
                generated.title,  # 已派發TopicTitle
                ", ".join(classification.persona_tags + classification.industry_tags + classification.event_tags + classification.stock_tags),  # 已派發TopicKeywords
                generated.content,  # 生成內容
                "ready_to_post",  # 發文狀態
                "2025-08-27 12:00:00",  # 上次排程時間
                "",  # 發文時間戳記
                "",  # 最近錯誤訊息
                "",  # 平台發文ID
                "",  # 平台發文URL
                topic.title  # 熱門話題標題
            ]
            
            post_records.append(record)
            print(f"✅ 準備發文記錄: {post_id} - {generated.title[:30]}...")
        
        # 步驟5: 寫入 Google Sheets
        print(f"\n步驟5: 寫入 Google Sheets ({len(post_records)} 筆記錄)...")
        
        if post_records:
            try:
                # 讀取現有數據以找到最後一行
                existing_data = sheets_client.read_sheet('貼文記錄表', 'A:R')
                start_row = len(existing_data) + 1
                
                # 寫入新記錄
                range_name = f'A{start_row}:R{start_row + len(post_records) - 1}'
                sheets_client.write_sheet('貼文記錄表', post_records, range_name)
                
                print(f"✅ 成功寫入 {len(post_records)} 筆準備發文記錄到 Google Sheets")
                print(f"   範圍: {range_name}")
                
                # 顯示寫入的記錄
                for i, record in enumerate(post_records, 1):
                    print(f"   {i}. {record[0]} - {record[2]} - {record[8]}")
                
            except Exception as e:
                print(f"❌ 寫入 Google Sheets 失敗: {e}")
        else:
            print("❌ 沒有準備發文的記錄")
        
        print("\n✅ 測試完成！")
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_post_records())
