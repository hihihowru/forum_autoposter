#!/usr/bin/env python3
"""
使用現有的 CMoney 客戶端測試文章互動數據獲取
"""

import asyncio
import sys
import os
from datetime import datetime

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.clients.cmoney.cmoney_client import CMoneyClient, LoginCredentials

async def test_cmoney_client():
    """測試 CMoney 客戶端"""
    
    print("🚀 測試 CMoney 客戶端")
    print("=" * 60)
    
    # 初始化客戶端
    client = CMoneyClient()
    
    # 測試文章 ID
    test_article_ids = [
        "173337593",  # 您提供的 ID
        "173337594",  # 相近的 ID
        "173337595",  # 相近的 ID
    ]
    
    print("📝 測試文章 ID 列表:")
    for i, article_id in enumerate(test_article_ids, 1):
        print(f"  {i}. {article_id}")
    
    print("\n" + "=" * 60)
    
    # 測試每個文章 ID
    for i, article_id in enumerate(test_article_ids, 1):
        print(f"\n📝 測試 {i}/{len(test_article_ids)}: Article ID {article_id}")
        print("-" * 40)
        
        try:
            # 使用現有的方法獲取互動數據
            # 注意：這裡需要有效的 access_token，我們先測試 API 端點
            print(f"🔗 API 端點: {client.api_base_url}/api/Article/{article_id}")
            
            # 模擬一個測試用的 access_token (實際使用時需要真實的 token)
            test_token = "test_token_for_api_endpoint_check"
            
            # 嘗試獲取互動數據
            interaction_data = await client.get_article_interactions(test_token, article_id)
            
            print(f"✅ 成功獲取互動數據:")
            print(f"  - 文章 ID: {interaction_data.post_id}")
            print(f"  - 會員 ID: {interaction_data.member_id}")
            print(f"  - 讚數: {interaction_data.likes}")
            print(f"  - 留言數: {interaction_data.comments}")
            print(f"  - 分享數: {interaction_data.shares}")
            print(f"  - 瀏覽數: {interaction_data.views}")
            print(f"  - 互動率: {interaction_data.engagement_rate}")
            
            # 檢查原始數據
            if interaction_data.raw_data:
                if "error" in interaction_data.raw_data:
                    print(f"⚠️ 錯誤信息: {interaction_data.raw_data['error']}")
                else:
                    print(f"📊 原始數據包含 {len(interaction_data.raw_data)} 個欄位")
                    # 顯示一些關鍵欄位
                    key_fields = ["commentCount", "interestedCount", "collectedCount", "emojiCount"]
                    for field in key_fields:
                        if field in interaction_data.raw_data:
                            print(f"  - {field}: {interaction_data.raw_data[field]}")
            
        except Exception as e:
            print(f"❌ 測試失敗: {e}")
    
    print("\n" + "=" * 60)
    print("📊 測試總結")
    print("=" * 60)
    
    print("💡 建議:")
    print("1. 確認 Article ID 是否有效")
    print("2. 檢查是否需要有效的 access_token")
    print("3. 驗證 API 端點是否正確")
    print("4. 檢查 CMoney API 的認證要求")

async def test_api_endpoint_directly():
    """直接測試 API 端點"""
    print("\n🔍 直接測試 API 端點")
    print("=" * 60)
    
    import httpx
    
    client = CMoneyClient()
    test_article_id = "173337593"
    
    # 測試不同的 API 端點
    api_endpoints = [
        f"{client.api_base_url}/api/Article/{test_article_id}",
        f"{client.api_base_url}/api/v1/Article/{test_article_id}",
        f"{client.api_base_url}/api/v2/Article/{test_article_id}",
        f"https://api.cmoney.tw/api/Article/{test_article_id}",
        f"https://api.cmoney.tw/api/v1/Article/{test_article_id}",
        f"https://api.cmoney.tw/api/v2/Article/{test_article_id}",
    ]
    
    headers = {
        "X-Version": "2.0",
        "cmoneyapi-trace-context": "dashboard-test",
        "accept": "application/json",
        "User-Agent": "Dashboard-Test/1.0"
    }
    
    async with httpx.AsyncClient() as http_client:
        for i, endpoint in enumerate(api_endpoints, 1):
            print(f"\n📝 測試端點 {i}/{len(api_endpoints)}: {endpoint}")
            print("-" * 50)
            
            try:
                response = await http_client.get(endpoint, headers=headers, timeout=10)
                print(f"📊 狀態碼: {response.status_code}")
                
                if response.status_code == 200:
                    print("✅ 成功！")
                    try:
                        data = response.json()
                        print(f"📄 響應數據類型: {type(data)}")
                        if isinstance(data, dict):
                            print(f"📋 包含欄位: {list(data.keys())[:10]}{'...' if len(data) > 10 else ''}")
                    except:
                        print("📄 響應不是 JSON 格式")
                elif response.status_code == 404:
                    print("❌ 404 - 文章不存在")
                elif response.status_code == 401:
                    print("❌ 401 - 需要認證")
                elif response.status_code == 403:
                    print("❌ 403 - 權限不足")
                else:
                    print(f"❌ 其他錯誤: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ 請求失敗: {e}")

def check_cmoney_config():
    """檢查 CMoney 配置"""
    print("\n🔧 檢查 CMoney 配置")
    print("=" * 60)
    
    client = CMoneyClient()
    
    print(f"📡 API 基礎 URL: {client.api_base_url}")
    print(f"🌐 客戶端配置: {client.client}")
    
    # 檢查環境變量
    env_vars = [
        "CMONEY_API_BASE_URL",
        "CMONEY_API_KEY", 
        "CMONEY_ACCESS_TOKEN",
        "FINLAB_API_KEY"
    ]
    
    print("\n📋 環境變量檢查:")
    for var in env_vars:
        value = os.getenv(var)
        if value:
            # 隱藏敏感信息
            if "KEY" in var or "TOKEN" in var:
                display_value = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "***"
            else:
                display_value = value
            print(f"  ✅ {var}: {display_value}")
        else:
            print(f"  ❌ {var}: 未設置")

async def main():
    """主函數"""
    print("🧪 CMoney 客戶端測試工具")
    print("=" * 60)
    print(f"⏰ 測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 檢查配置
    check_cmoney_config()
    
    # 2. 測試客戶端
    await test_cmoney_client()
    
    # 3. 直接測試 API 端點
    await test_api_endpoint_directly()
    
    print("\n✅ 測試完成！")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
