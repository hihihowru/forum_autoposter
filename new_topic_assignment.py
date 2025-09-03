#!/usr/bin/env python3
"""
新話題分派和發文系統
使用新的 post ID 邏輯：topic_id + kol_serial
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
from src.services.publish.publish_service import PublishService

async def main():
    """新話題分派和發文主流程"""
    
    print("=== 新話題分派和發文系統 ===\n")
    
    # 初始化服務
    sheets_client = GoogleSheetsClient(
        credentials_file=os.getenv('GOOGLE_CREDENTIALS_FILE'),
        spreadsheet_id=os.getenv('GOOGLE_SHEETS_ID')
    )
    
    cmoney_client = CMoneyClient()
    assignment_service = AssignmentService(sheets_client)
    topic_classifier = TopicClassifier()
    content_generator = ContentGenerator()
    publish_service = PublishService(sheets_client)
    
    try:
        # 步驟1: 獲取熱門話題
        print("步驟1: 獲取熱門話題...")
        credentials = LoginCredentials(
            email='forum_200@cmoney.com.tw',
            password='N9t1kY3x'
        )
        
        token = await cmoney_client.login(credentials)
        topics = await cmoney_client.get_trending_topics(token.token)
        
        print(f"✅ 獲取到 {len(topics)} 個熱門話題")
        
        # 顯示話題列表
        for i, topic in enumerate(topics[:5], 1):  # 只顯示前5個
            print(f"  {i}. {topic.title}")
            print(f"     ID: {topic.id}")
            print(f"     Name: {topic.name}")
            print()
        
        # 步驟2: 話題分類
        print("步驟2: 話題分類...")
        classified_topics = []
        
        for topic in topics[:3]:  # 只處理前3個話題
            print(f"分類話題: {topic.title}")
            classification = topic_classifier.classify_topic(topic.id, topic.title, topic.name)
            classified_topics.append({
                'id': topic.id,
                'title': topic.title,
                'name': topic.name,
                'classification': classification
            })
            print(f"  分類結果: {classification.persona_tags}, {classification.industry_tags}")
        
        # 步驟3: KOL 分派
        print("\n步驟3: KOL 分派...")
        assignment_service.load_kol_profiles()
        print(f"✅ 載入了 {len(assignment_service._kol_profiles)} 個 KOL")
        
        # 顯示可用的 KOL
        active_kols = [kol for kol in assignment_service._kol_profiles if kol.enabled]
        print(f"✅ 有 {len(active_kols)} 個活躍的 KOL")
        
        for kol in active_kols[:5]:  # 只顯示前5個
            print(f"  - {kol.nickname} (Serial: {kol.serial}) - {kol.persona}")
        
        # 步驟4: 內容生成
        print("\n步驟4: 內容生成...")
        generated_posts = []
        
        for topic_data in classified_topics:
            # 為每個話題分派 KOL
            topic_data_obj = TopicData(
                topic_id=topic_data['id'],
                title=topic_data['title'],
                input_index=0,
                persona_tags=topic_data['classification'].persona_tags,
                industry_tags=topic_data['classification'].industry_tags,
                event_tags=topic_data['classification'].event_tags,
                stock_tags=topic_data['classification'].stock_tags,
                classification=topic_data['classification']
            )
            
            topic_assignments = assignment_service.assign_topics([topic_data_obj], max_assignments_per_topic=2)  # 每個話題最多2個KOL
            
            print(f"\n話題: {topic_data['title']}")
            print(f"分派給 {len(topic_assignments)} 個 KOL")
            
            for assignment in topic_assignments:
                # 找到對應的 KOL
                kol = next((k for k in assignment_service._kol_profiles if k.serial == assignment.kol_serial), None)
                if not kol:
                    continue
                
                print(f"  - {kol.nickname} (Serial: {assignment.kol_serial})")
                
                # 生成內容
                content_request = ContentRequest(
                    topic_title=topic_data['title'],
                    topic_keywords=", ".join(topic_data['classification'].persona_tags + 
                                           topic_data['classification'].industry_tags + 
                                           topic_data['classification'].event_tags),
                    kol_persona=kol.persona,
                    kol_nickname=kol.nickname,
                    content_type="investment",
                    target_audience="active_traders"
                )
                
                generated = content_generator.generate_complete_content(content_request)
                
                if generated.success:
                    # 生成新的 post ID: topic_id + kol_serial
                    post_id = f"{topic_data['id']}-{assignment.kol_serial}"
                    
                    post_data = {
                        'post_id': post_id,
                        'topic_id': topic_data['id'],
                        'topic_title': topic_data['title'],
                        'kol_serial': assignment.kol_serial,
                        'kol_nickname': kol.nickname,
                        'kol_persona': kol.persona,
                        'generated_title': generated.title,
                        'generated_content': generated.content,
                        'classification': topic_data['classification']
                    }
                    
                    generated_posts.append(post_data)
                    print(f"    ✅ 生成成功: {generated.title[:30]}...")
                else:
                    print(f"    ❌ 生成失敗: {generated.error_message}")
        
        # 步驟5: 顯示準備發文的內容
        print(f"\n步驟5: 準備發文內容 ({len(generated_posts)} 篇)")
        print("=" * 80)
        
        for i, post in enumerate(generated_posts, 1):
            print(f"\n【第 {i} 篇】")
            print(f"Post ID: {post['post_id']}")
            print(f"KOL: {post['kol_nickname']} ({post['kol_persona']})")
            print(f"話題: {post['topic_title']}")
            print(f"標題: {post['generated_title']}")
            print(f"內容長度: {len(post['generated_content'])} 字")
            print(f"內容預覽: {post['generated_content'][:100]}...")
            print("-" * 40)
        
        # 步驟6: 確認是否發文
        print(f"\n準備發文 {len(generated_posts)} 篇文章")
        confirm = input("是否開始發文？(y/N): ").strip().lower()
        
        if confirm == 'y':
            print("\n步驟6: 開始發文...")
            
            # 登入 KOL
            kol_credentials = {
                200: {"email": "forum_200@cmoney.com.tw", "password": "N9t1kY3x"},
                201: {"email": "forum_201@cmoney.com.tw", "password": "m7C1lR4t"},
                202: {"email": "forum_202@cmoney.com.tw", "password": "x2U9nW5p"}
            }
            
            # 登入需要的 KOL
            kol_serials = list(set([post['kol_serial'] for post in generated_posts]))
            for kol_serial in kol_serials:
                if kol_serial in kol_credentials:
                    print(f"登入 KOL {kol_serial}...")
                    success = await publish_service.login_kol(
                        kol_serial,
                        kol_credentials[kol_serial]["email"],
                        kol_credentials[kol_serial]["password"]
                    )
                    if success:
                        print(f"✅ KOL {kol_serial} 登入成功")
                    else:
                        print(f"❌ KOL {kol_serial} 登入失敗")
            
            # 發文
            success_count = 0
            for i, post in enumerate(generated_posts, 1):
                print(f"\n發文第 {i} 篇: {post['post_id']}")
                
                result = await publish_service.publish_post(
                    kol_serial=post['kol_serial'],
                    title=post['generated_title'],
                    content=post['generated_content'],
                    topic_id=post['topic_id']
                )
                
                if result and result.success:
                    print(f"✅ 發文成功: {result.post_id}")
                    success_count += 1
                else:
                    print(f"❌ 發文失敗: {result.error_message if result else 'Unknown error'}")
                
                # 間隔2分鐘
                if i < len(generated_posts):
                    print("等待 2 分鐘...")
                    await asyncio.sleep(120)
            
            print(f"\n✅ 發文完成！成功發文 {success_count}/{len(generated_posts)} 篇")
        else:
            print("取消發文")
        
    except Exception as e:
        print(f"❌ 流程失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
