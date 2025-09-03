#!/usr/bin/env python3
"""
測試發文流程：檢查發文前後 Google Sheets 的狀態
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

async def test_publish_flow():
    """測試發文流程"""
    
    print("=== 測試發文流程 ===\n")
    
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
        # 步驟1: 檢查發文前的 Google Sheets 狀態
        print("步驟1: 檢查發文前的 Google Sheets 狀態...")
        ready_posts_before = publish_service.get_ready_to_post_records()
        print(f"發文前準備發文的記錄: {len(ready_posts_before)} 筆")
        
        for post in ready_posts_before:
            print(f"  - {post['post_id']} - {post['kol_nickname']} - 狀態: ready_to_post")
        
        if not ready_posts_before:
            print("❌ 沒有準備發文的記錄，無法測試發文流程")
            return
        
        # 步驟2: 只登入需要的 KOL
        print(f"\n步驟2: 登入需要的 KOL...")
        needed_serials = set(post['kol_serial'] for post in ready_posts_before)
        print(f"需要登入的 KOL: {needed_serials}")
        
        # 讀取 KOL 配置
        data = sheets_client.read_sheet('同學會帳號管理', 'A:Z')
        headers = data[0]
        kol_data = data[1:]
        
        # 找到相關列的索引
        serial_idx = headers.index('序號') if '序號' in headers else 0
        email_idx = headers.index('Email(帳號)') if 'Email(帳號)' in headers else 5
        password_idx = headers.index('密碼') if '密碼' in headers else 6
        status_idx = headers.index('狀態') if '狀態' in headers else 9
        
        login_success_count = 0
        for row in kol_data:
            if len(row) > max(serial_idx, email_idx, password_idx, status_idx):
                serial = int(row[serial_idx]) if row[serial_idx] else 0
                email = row[email_idx] if row[email_idx] else ''
                password = row[password_idx] if row[password_idx] else ''
                status = row[status_idx] if row[status_idx] else ''
                
                if serial in needed_serials and serial > 0 and email and password and status == 'active':
                    print(f"登入 KOL {serial} ({email})...")
                    success = await publish_service.login_kol(serial, email, password)
                    if success:
                        print(f"  ✅ 登入成功")
                        login_success_count += 1
                    else:
                        print(f"  ❌ 登入失敗")
        
        if login_success_count == 0:
            print("❌ 沒有 KOL 登入成功")
            return
        
        print(f"✅ {login_success_count} 個 KOL 登入成功")
        
        # 步驟3: 選擇第一篇準備發文的記錄進行測試
        test_post = ready_posts_before[0]
        print(f"\n步驟3: 選擇測試貼文...")
        print(f"  Post ID: {test_post['post_id']}")
        print(f"  KOL: {test_post['kol_nickname']} (Serial: {test_post['kol_serial']})")
        print(f"  標題: {test_post['title']}")
        print(f"  內容: {test_post['content'][:100]}...")
        
        # 檢查這個 KOL 是否已登入
        if test_post['kol_serial'] not in publish_service.kol_tokens:
            print(f"❌ KOL {test_post['kol_serial']} 未登入")
            return
        
        # 步驟4: 發文
        print(f"\n步驟4: 發文...")
        result = await publish_service.publish_post(
            kol_serial=test_post['kol_serial'],
            title=test_post['title'],
            content=test_post['content'],
            topic_id=test_post['topic_id']
        )
        
        if result and result.success:
            print(f"✅ 發文成功!")
            print(f"   Article ID: {result.post_id}")
            print(f"   Article URL: {result.post_url}")
            
            # 步驟5: 手動更新 Google Sheets
            print(f"\n步驟5: 更新 Google Sheets...")
            post_result = {
                'post_id': test_post['post_id'],
                'kol_serial': test_post['kol_serial'],
                'success': True,
                'article_id': result.post_id,
                'article_url': result.post_url,
                'error_message': None
            }
            
            await publish_service._update_post_result(post_result)
            print(f"✅ 已更新 Google Sheets 記錄")
            
            # 步驟6: 檢查發文後的 Google Sheets 狀態
            print(f"\n步驟6: 檢查發文後的 Google Sheets 狀態...")
            ready_posts_after = publish_service.get_ready_to_post_records()
            print(f"發文後準備發文的記錄: {len(ready_posts_after)} 筆")
            
            # 檢查是否還包含剛才發文的記錄
            still_ready = any(post['post_id'] == test_post['post_id'] for post in ready_posts_after)
            if still_ready:
                print(f"❌ 發文記錄仍然在 ready_to_post 狀態")
            else:
                print(f"✅ 發文記錄已從 ready_to_post 狀態移除")
            
            # 讀取完整的貼文記錄表來檢查狀態
            print(f"\n步驟7: 檢查完整貼文記錄表...")
            try:
                data = sheets_client.read_sheet('貼文記錄表', 'A:R')
                for i, row in enumerate(data[1:], 1):  # 跳過標題行
                    if len(row) > 0 and row[0] == test_post['post_id']:
                        print(f"找到發文記錄:")
                        print(f"  行號: {i+1}")
                        print(f"  Post ID: {row[0]}")
                        print(f"  KOL Serial: {row[1]}")
                        print(f"  KOL 暱稱: {row[2]}")
                        print(f"  發文狀態: {row[11] if len(row) > 11 else 'N/A'}")
                        print(f"  發文時間: {row[13] if len(row) > 13 else 'N/A'}")
                        print(f"  Article ID: {row[15] if len(row) > 15 else 'N/A'}")
                        print(f"  Article URL: {row[16] if len(row) > 16 else 'N/A'}")
                        break
                else:
                    print(f"❌ 在貼文記錄表中找不到 Post ID: {test_post['post_id']}")
                    
            except Exception as e:
                print(f"❌ 讀取貼文記錄表失敗: {e}")
            
        else:
            print(f"❌ 發文失敗: {result.error_message if result else 'Unknown error'}")
        
        print("\n✅ 發文流程測試完成！")
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_publish_flow())
