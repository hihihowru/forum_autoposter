#!/usr/bin/env python3
"""
測試 CMoney Topic API 的腳本
用於測試獲取特定話題的相關股票資訊
"""
import os
import asyncio
import httpx
import json
from datetime import datetime
from src.clients.cmoney.cmoney_client import CMoneyClient, LoginCredentials

async def test_topic_trending_api():
    """測試話題趨勢 API"""
    
    # 測試用的話題 ID
    topic_id = "136405de-3cfb-4112-8124-af4f0d42bdd8"
    
    print("🔍 測試 CMoney Topic API")
    print("=" * 50)
    print(f"話題 ID: {topic_id}")
    print(f"API 端點: https://forumservice.cmoney.tw/api/Topic/{topic_id}/Trending")
    print()
    
    # 方法 1: 使用現有的 JWT token (可能已過期)
    print("📋 方法 1: 使用提供的 JWT token")
    print("-" * 30)
    
    jwt_token = "eyJhbGciOiJSUzI1NiIsImtpZCI6IkEydWczbUIxRFQiLCJ0eXAiOiJKV1QifQ.eyJzdWIiOiIxOTcxOTk3NyIsInVzZXJfZ3VpZCI6IjI3YWViYjk1LTg3NjQtNDE4ZC1hZDFlLTlhZDUzZjFmM2FhNyIsInRva2VuX2lkIjoiMTgiLCJhcHBfaWQiOiIxOCIsImlzX2d1ZXN0IjpmYWxzZSwibmJmIjoxNzU2MDM0OTUwLCJleHAiOjE3NTYxMjQ5NTAsImlhdCI6MTc1NjAzODU1MCwiaXNzIjoiaHR0cHM6Ly93d3cuY21vbmV5LnR3IiwiYXVkIjoiY21vbmV5YXBpIn0.q55F9IWTSBt9eA6CrrF4LlNSzH5oAep4d6Fb0XOljI7g7WCNjqoj10Ez297t70i-Dr9BqYrVaRELT7BJIWfh6folvm17kQ5-ZIqE8kk4ixRZTSxTVH5JQAWGFbUJsAbM4c8frDAvPFdVXww5PfPlhXEd9kdz9LOfJwnAk-qKXqB61dtGZqDvINIZZGs-qaAv7z_N3xU0y2OZMiqwMhqPh9oda7yAxxmoejTNhveE0PVBXa3OUksYMp8Ymz0cBabLh9hlEoFZclusXsNsU__FER44JyAuwQYs2r9NiLxwTXoaA3v3ybfik1w2LeT6JyaOpAmIV_ecTwLqX48ACO4BmA"
    
    headers = {
        "X-Version": "2.0",
        "Accept-Encoding": "gzip",
        "cmoneyapi-trace-context": "testing",
        "Authorization": f"Bearer {jwt_token}"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://forumservice.cmoney.tw/api/Topic/{topic_id}/Trending",
                headers=headers,
                timeout=30.0
            )
            
            print(f"狀態碼: {response.status_code}")
            print(f"回應標頭: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ 成功獲取數據!")
                print(f"回應內容: {json.dumps(data, indent=2, ensure_ascii=False)}")
            else:
                print(f"❌ 請求失敗: {response.text}")
                
    except Exception as e:
        print(f"❌ 請求異常: {e}")
    
    print()
    
    # 方法 2: 使用 CMoneyClient 進行登入並測試
    print("📋 方法 2: 使用 CMoneyClient 登入")
    print("-" * 30)
    
    # 檢查環境變數
    email = os.getenv("CMONEY_EMAIL")
    password = os.getenv("CMONEY_PASSWORD")
    
    if not email or not password:
        print("⚠️  未設定 CMONEY_EMAIL 或 CMONEY_PASSWORD 環境變數")
        print("請設定以下環境變數:")
        print("export CMONEY_EMAIL='your_email@example.com'")
        print("export CMONEY_PASSWORD='your_password'")
        print()
        print("或者直接在腳本中設定:")
        print("email = 'your_email@example.com'")
        print("password = 'your_password'")
        return
    
    try:
        # 創建客戶端並登入
        client = CMoneyClient()
        credentials = LoginCredentials(email=email, password=password)
        
        print(f"正在登入: {email}")
        access_token = await client.login(credentials)
        print(f"✅ 登入成功! Token: {access_token.token[:50]}...")
        
        # 測試話題趨勢 API
        print(f"正在測試話題趨勢 API...")
        
        headers = {
            "Authorization": f"Bearer {access_token.token}",
            "X-Version": "2.0",
            "Accept-Encoding": "gzip",
            "cmoneyapi-trace-context": "testing"
        }
        
        async with httpx.AsyncClient() as http_client:
            response = await http_client.get(
                f"https://forumservice.cmoney.tw/api/Topic/{topic_id}/Trending",
                headers=headers,
                timeout=30.0
            )
            
            print(f"狀態碼: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ 成功獲取話題趨勢數據!")
                print(f"回應內容: {json.dumps(data, indent=2, ensure_ascii=False)}")
                
                # 分析回應數據
                if isinstance(data, dict):
                    print("\n📊 數據分析:")
                    for key, value in data.items():
                        print(f"  {key}: {type(value).__name__}")
                        if isinstance(value, (list, dict)) and len(str(value)) < 200:
                            print(f"    內容: {value}")
                        elif isinstance(value, (list, dict)):
                            print(f"    內容: {str(value)[:100]}...")
                        else:
                            print(f"    內容: {value}")
                            
            else:
                print(f"❌ 請求失敗: {response.text}")
                
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if 'client' in locals():
            client.close()

async def test_alternative_endpoints():
    """測試其他可能的 API 端點"""
    
    topic_id = "136405de-3cfb-4112-8124-af4f0d42bdd8"
    
    print("\n🔍 測試其他可能的 API 端點")
    print("=" * 50)
    
    # 可能的端點列表
    endpoints = [
        f"/api/Topic/{topic_id}",
        f"/api/Topic/{topic_id}/Articles",
        f"/api/Topic/{topic_id}/Stocks",
        f"/api/Topic/{topic_id}/Related",
        f"/api/Topic/{topic_id}/Info"
    ]
    
    # 使用提供的 JWT token
    jwt_token = "eyJhbGciOiJSUzI1NiIsImtpZCI6IkEydWczbUIxRFQiLCJ0eXAiOiJKV1QifQ.eyJzdWIiOiIxOTcxOTk3NyIsInVzZXJfZ3VpZCI6IjI3YWViYjk1LTg3NjQtNDE4ZC1hZDFlLTlhZDUzZjFmM2FhNyIsInRva2VuX2lkIjoiMTgiLCJhcHBfaWQiOiIxOCIsImlzX2d1ZXN0IjpmYWxzZSwibmJmIjoxNzU2MDM0OTUwLCJleHAiOjE3NTYxMjQ5NTAsImlhdCI6MTc1NjAzODU1MCwiaXNzIjoiaHR0cHM6Ly93d3cuY21vbmV5LnR3IiwiYXVkIjoiY21vbmV5YXBpIn0.q55F9IWTSBt9eA6CrrF4LlNSzH5oAep4d6Fb0XOljI7g7WCNjqoj10Ez297t70i-Dr9BqYrVaRELT7BJIWfh6folvm17kQ5-ZIqE8kk4ixRZTSxTVH5JQAWGFbUJsAbM4c8frDAvPFdVXww5PfPlhXEd9kdz9LOfJwnAk-qKXqB61dtGZqDvINIZZGs-qaAv7z_N3xU0y2OZMiqwMhqPh9oda7yAxxmoejTNhveE0PVBXa3OUksYMp8Ymz0cBabLh9hlEoFZclusXsNsU__FER44JyAuwQYs2r9NiLxwTXoaA3v3ybfik1w2LeT6JyaOpAmIV_ecTwLqX48ACO4BmA"
    
    headers = {
        "X-Version": "2.0",
        "Accept-Encoding": "gzip",
        "cmoneyapi-trace-context": "testing",
        "Authorization": f"Bearer {jwt_token}"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            for endpoint in endpoints:
                url = f"https://forumservice.cmoney.tw{endpoint}"
                print(f"\n測試端點: {endpoint}")
                
                try:
                    response = await client.get(url, headers=headers, timeout=10.0)
                    print(f"  狀態碼: {response.status_code}")
                    
                    if response.status_code == 200:
                        data = response.json()
                        print(f"  ✅ 成功! 回應長度: {len(str(data))} 字元")
                        if len(str(data)) < 500:
                            print(f"  內容: {json.dumps(data, indent=2, ensure_ascii=False)}")
                    else:
                        print(f"  ❌ 失敗: {response.text[:100]}")
                        
                except Exception as e:
                    print(f"  ❌ 異常: {e}")
                    
    except Exception as e:
        print(f"❌ 測試異常: {e}")

if __name__ == "__main__":
    print("🚀 開始測試 CMoney Topic API")
    print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 執行測試
    asyncio.run(test_topic_trending_api())
    asyncio.run(test_alternative_endpoints())
    
    print("\n✅ 測試完成!")



