#!/usr/bin/env python3
"""
貼文生成調試腳本
用於追蹤貼文生成的完整流程
"""

import requests
import json
import time
from datetime import datetime

def test_post_generation():
    """測試貼文生成流程"""
    
    print("🔍 開始測試貼文生成流程...")
    
    # 1. 測試後端 API 連接
    print("\n1️⃣ 測試後端 API 連接...")
    try:
        response = requests.get("http://localhost:8001/posts", timeout=10)
        print(f"✅ 後端 API 連接正常: {response.status_code}")
    except Exception as e:
        print(f"❌ 後端 API 連接失敗: {e}")
        return
    
    # 2. 測試貼文生成 API
    print("\n2️⃣ 測試貼文生成 API...")
    test_data = {
        "stock_code": "2330",
        "stock_name": "台積電",
        "kol_serial": "200",
        "kol_persona": "technical",
        "content_style": "chart_analysis",
        "target_audience": "active_traders",
        "auto_post": False,
        "batch_mode": True,
        "session_id": int(time.time() * 1000),  # 使用當前時間戳作為 session_id
        "content_length": "medium",
        "max_words": 200,
        "data_sources": {},
        "explainability_config": {},
        "news_config": {},
        "tags_config": {},
        "topic_id": None,
        "topic_title": None
    }
    
    try:
        print(f"📤 發送測試請求: session_id={test_data['session_id']}")
        response = requests.post(
            "http://localhost:8001/post/manual",
            json=test_data,
            timeout=60
        )
        
        print(f"📥 後端響應狀態: {response.status_code}")
        print(f"📥 後端響應內容: {response.text[:500]}...")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 貼文生成成功: {result.get('post_id')}")
            
            # 3. 驗證貼文是否保存到數據庫
            print("\n3️⃣ 驗證貼文是否保存到數據庫...")
            session_id = test_data['session_id']
            
            # 等待一下讓數據庫操作完成
            time.sleep(2)
            
            check_response = requests.get(f"http://localhost:8001/posts/session/{session_id}")
            if check_response.status_code == 200:
                check_result = check_response.json()
                posts = check_result.get('posts', [])
                print(f"📊 數據庫中的貼文數量: {len(posts)}")
                
                if len(posts) > 0:
                    print("✅ 貼文已成功保存到數據庫")
                    print(f"📝 貼文詳情: {posts[0].get('title', '無標題')}")
                else:
                    print("❌ 貼文未保存到數據庫")
                    print("🔍 可能的原因:")
                    print("  - 數據庫事務未提交")
                    print("  - 數據庫連接問題")
                    print("  - 數據驗證失敗")
            else:
                print(f"❌ 檢查數據庫失敗: {check_response.status_code}")
        else:
            print(f"❌ 貼文生成失敗: {response.status_code}")
            print(f"錯誤詳情: {response.text}")
            
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        print(f"錯誤堆疊: {traceback.format_exc()}")

if __name__ == "__main__":
    test_post_generation()
