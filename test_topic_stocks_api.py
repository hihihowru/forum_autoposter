#!/usr/bin/env python3
"""
測試 CMoney Topic API 獲取相關股票資訊
使用專案中現有的 CMoneyClient 來正確處理認證
"""
import sys
import asyncio
import os
import json
import httpx
from pathlib import Path
from datetime import datetime

# 添加 src 目錄到 Python 路徑
sys.path.append(str(Path(__file__).parent / "src"))

from clients.cmoney.cmoney_client import CMoneyClient, LoginCredentials
from clients.google.sheets_client import GoogleSheetsClient

async def test_topic_stocks_api():
    """測試話題相關股票 API"""
    
    # 測試用的話題 ID
    topic_id = "136405de-3cfb-4112-8124-af4f0d42bdd8"
    
    print("🔍 測試 CMoney Topic API 獲取相關股票")
    print("=" * 60)
    print(f"話題 ID: {topic_id}")
    print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # 1. 初始化客戶端
        cmoney_client = CMoneyClient()
        sheets_client = GoogleSheetsClient(
            credentials_file="./credentials/google-service-account.json",
            spreadsheet_id="148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LikN2s"
        )
        
        # 2. 從 Google Sheets 讀取 KOL 憑證
        print("📋 讀取 KOL 憑證...")
        try:
            kol_data = sheets_client.read_sheet('同學會帳號管理', 'A:Z')
            
            if len(kol_data) < 2:
                print("❌ 沒有找到 KOL 數據")
                return False
            
            # 找到第一個有效的 KOL 憑證
            headers = kol_data[0]
            email_idx = None
            password_idx = None
            
            for i, header in enumerate(headers):
                if 'Email' in header or '帳號' in header:
                    email_idx = i
                elif '密碼' in header:
                    password_idx = i
            
            if email_idx is None or password_idx is None:
                print("❌ 找不到 Email 或密碼欄位")
                return False
            
            # 使用第一個 KOL 的憑證
            first_kol = kol_data[1]
            email = first_kol[email_idx] if len(first_kol) > email_idx else None
            password = first_kol[password_idx] if len(first_kol) > password_idx else None
            
            if not email or not password:
                print("❌ KOL 憑證不完整")
                return False
            
            print(f"✅ 使用 KOL 憑證: {email[:5]}***@{email.split('@')[1] if '@' in email else '***'}")
            
        except Exception as e:
            print(f"❌ 讀取 Google Sheets 失敗: {e}")
            print("請確認 Google Sheets 憑證和設定正確")
            return False
        
        # 3. 登入 CMoney
        print("\n🔐 登入 CMoney...")
        credentials = LoginCredentials(email=email, password=password)
        access_token = await cmoney_client.login(credentials)
        print(f"✅ 登入成功，Token: {access_token.token[:30]}...")
        
        # 4. 測試不同的 API 端點
        print(f"\n🌐 測試話題相關 API 端點...")
        
        # 可能的端點列表
        endpoints_to_test = [
            f"/api/Topic/{topic_id}/Trending",
            f"/api/Topic/{topic_id}",
            f"/api/Topic/{topic_id}/Articles", 
            f"/api/Topic/{topic_id}/Stocks",
            f"/api/Topic/{topic_id}/Related",
            f"/api/Topic/{topic_id}/Info",
            f"/api/Topic/{topic_id}/Details"
        ]
        
        headers = {
            "Authorization": f"Bearer {access_token.token}",
            "X-Version": "2.0",
            "Accept-Encoding": "gzip",
            "cmoneyapi-trace-context": "testing"
        }
        
        successful_endpoints = []
        
        async with httpx.AsyncClient() as client:
            for endpoint in endpoints_to_test:
                url = f"https://forumservice.cmoney.tw{endpoint}"
                print(f"\n測試端點: {endpoint}")
                
                try:
                    response = await client.get(url, headers=headers, timeout=15.0)
                    print(f"  狀態碼: {response.status_code}")
                    
                    if response.status_code == 200:
                        data = response.json()
                        print(f"  ✅ 成功! 回應長度: {len(str(data))} 字元")
                        successful_endpoints.append((endpoint, data))
                        
                        # 顯示回應內容摘要
                        if isinstance(data, dict):
                            print(f"  回應欄位: {list(data.keys())}")
                            # 檢查是否包含股票相關資訊
                            stock_related_keys = ['stocks', 'stock_ids', 'stockSymbols', 'relatedStocks', 'commodityTags']
                            found_stock_keys = [key for key in stock_related_keys if key in data]
                            if found_stock_keys:
                                print(f"  🎯 找到股票相關欄位: {found_stock_keys}")
                                for key in found_stock_keys:
                                    print(f"    {key}: {data[key]}")
                        elif isinstance(data, list):
                            print(f"  回應類型: 陣列，長度: {len(data)}")
                            if data and isinstance(data[0], dict):
                                print(f"  第一個項目欄位: {list(data[0].keys())}")
                        
                        # 如果回應不太長，顯示完整內容
                        if len(str(data)) < 1000:
                            print(f"  完整回應: {json.dumps(data, indent=2, ensure_ascii=False)}")
                        else:
                            print(f"  回應預覽: {str(data)[:500]}...")
                            
                    elif response.status_code == 401:
                        print(f"  ❌ 認證失敗 (Token 可能過期)")
                    elif response.status_code == 404:
                        print(f"  ❌ 端點不存在")
                    else:
                        print(f"  ❌ 失敗: {response.text[:100]}")
                        
                except Exception as e:
                    print(f"  ❌ 異常: {e}")
        
        # 5. 分析成功的端點
        if successful_endpoints:
            print(f"\n🎉 找到 {len(successful_endpoints)} 個有效的 API 端點!")
            print("=" * 50)
            
            for endpoint, data in successful_endpoints:
                print(f"\n📊 端點: {endpoint}")
                print(f"數據摘要: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}...")
                
                # 嘗試提取股票相關資訊
                stocks_found = extract_stock_information(data)
                if stocks_found:
                    print(f"🎯 找到股票資訊: {stocks_found}")
                else:
                    print("ℹ️  未找到明顯的股票相關資訊")
        else:
            print(f"\n❌ 沒有找到有效的 API 端點")
            print("可能的原因:")
            print("1. API 端點路徑不正確")
            print("2. 話題 ID 不存在或無效")
            print("3. API 版本或格式已變更")
            print("4. 需要額外的權限或參數")
        
        # 6. 測試獲取一般熱門話題
        print(f"\n📈 測試獲取一般熱門話題...")
        try:
            trending_topics = await cmoney_client.get_trending_topics(access_token.token)
            print(f"✅ 成功獲取 {len(trending_topics)} 個熱門話題")
            
            if trending_topics:
                print("前 3 個話題:")
                for i, topic in enumerate(trending_topics[:3], 1):
                    print(f"  {i}. ID: {topic.id}")
                    print(f"     標題: {topic.title}")
                    print(f"     名稱: {topic.name}")
                    if topic.last_article_create_time:
                        print(f"     最後文章時間: {topic.last_article_create_time}")
                    print()
        except Exception as e:
            print(f"❌ 獲取熱門話題失敗: {e}")
        
        return len(successful_endpoints) > 0
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def extract_stock_information(data):
    """從 API 回應中提取股票相關資訊"""
    stocks_found = []
    
    def search_stocks(obj, path=""):
        if isinstance(obj, dict):
            for key, value in obj.items():
                current_path = f"{path}.{key}" if path else key
                
                # 檢查是否為股票相關欄位
                if any(keyword in key.lower() for keyword in ['stock', 'symbol', 'code', 'id']):
                    if isinstance(value, (str, int)):
                        stocks_found.append(f"{current_path}: {value}")
                    elif isinstance(value, list):
                        stocks_found.append(f"{current_path}: {value}")
                
                # 遞歸搜尋
                search_stocks(value, current_path)
                
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                search_stocks(item, f"{path}[{i}]")
    
    search_stocks(data)
    return stocks_found

async def test_alternative_approaches():
    """測試其他可能的方法"""
    print(f"\n🔍 測試其他可能的方法...")
    print("=" * 50)
    
    # 方法 1: 檢查是否有其他 API 版本
    print("方法 1: 測試不同的 API 版本")
    topic_id = "136405de-3cfb-4112-8124-af4f0d42bdd8"
    
    versions = ["1.0", "2.0", "3.0"]
    headers_base = {
        "Accept-Encoding": "gzip",
        "cmoneyapi-trace-context": "testing"
    }
    
    # 這裡需要有效的 token，所以先跳過
    print("需要有效的 access token 才能測試不同版本")
    
    # 方法 2: 檢查是否有 GraphQL 端點
    print("\n方法 2: 檢查 GraphQL 端點")
    print("CMoney 可能使用 GraphQL 來查詢話題相關資訊")
    
    # 方法 3: 建議的替代方案
    print("\n方法 3: 建議的替代方案")
    print("1. 使用 /api/Topic/Trending 獲取所有熱門話題")
    print("2. 從話題列表中篩選包含股票資訊的話題")
    print("3. 使用文章 API 獲取話題下的文章，從文章中提取股票資訊")
    print("4. 整合 Finlab API 來獲取股票相關數據")

if __name__ == "__main__":
    print("🚀 開始測試 CMoney Topic API")
    print()
    
    # 執行主要測試
    success = asyncio.run(test_topic_stocks_api())
    
    # 執行其他方法測試
    asyncio.run(test_alternative_approaches())
    
    print(f"\n{'✅ 測試完成!' if success else '❌ 測試失敗!'}")
    if not success:
        print("\n建議:")
        print("1. 檢查話題 ID 是否正確")
        print("2. 確認 API 端點路徑")
        print("3. 聯繫 CMoney API 支援團隊")
        print("4. 考慮使用替代的數據來源")



