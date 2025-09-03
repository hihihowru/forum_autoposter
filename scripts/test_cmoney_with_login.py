#!/usr/bin/env python3
"""
使用登入功能測試 CMoney API 獲取文章互動數據
"""

import asyncio
import sys
import os
from datetime import datetime

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.clients.cmoney.cmoney_client import CMoneyClient, LoginCredentials

async def test_cmoney_with_login():
    """使用登入功能測試 CMoney API"""
    
    print("🚀 測試 CMoney API (含登入功能)")
    print("=" * 60)
    
    # 初始化客戶端
    client = CMoneyClient()
    
    # 測試文章 ID
    test_article_id = "173337593"
    
    print(f"📝 測試文章 ID: {test_article_id}")
    print(f"🔗 API 端點: {client.api_base_url}/api/Article/{test_article_id}")
    
    # 檢查環境變量中的登入憑證
    email = os.getenv("CMONEY_EMAIL")
    password = os.getenv("CMONEY_PASSWORD")
    
    if not email or not password:
        print("\n⚠️ 未找到登入憑證")
        print("請設置環境變量:")
        print("  export CMONEY_EMAIL='your_email@example.com'")
        print("  export CMONEY_PASSWORD='your_password'")
        print("\n或者直接在代碼中設置:")
        print("  email = 'your_email@example.com'")
        print("  password = 'your_password'")
        
        # 使用測試憑證 (請替換為真實憑證)
        email = "test@example.com"  # 請替換為真實的 email
        password = "test_password"  # 請替換為真實的 password
        
        print(f"\n🔧 使用測試憑證: {email}")
        print("⚠️ 注意：這可能會失敗，請使用真實憑證")
    
    # 創建登入憑證
    credentials = LoginCredentials(email=email, password=password)
    
    try:
        print(f"\n🔐 嘗試登入: {email}")
        print("-" * 40)
        
        # 登入獲取 access_token
        access_token = await client.login(credentials)
        
        print(f"✅ 登入成功！")
        print(f"📋 Token: {access_token.token[:20]}...{access_token.token[-10:]}")
        print(f"⏰ 過期時間: {access_token.expires_at}")
        print(f"🔄 是否過期: {access_token.is_expired}")
        
        print(f"\n📊 獲取文章互動數據...")
        print("-" * 40)
        
        # 獲取文章互動數據
        interaction_data = await client.get_article_interactions(access_token.token, test_article_id)
        
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
                print(f"\n📊 原始數據分析:")
                print(f"  - 包含 {len(interaction_data.raw_data)} 個欄位")
                
                # 顯示關鍵欄位
                key_fields = [
                    "commentCount", "interestedCount", "collectedCount", 
                    "emojiCount", "creatorId", "title", "content"
                ]
                
                for field in key_fields:
                    if field in interaction_data.raw_data:
                        value = interaction_data.raw_data[field]
                        if field == "emojiCount" and isinstance(value, dict):
                            print(f"  - {field}: {len(value)} 種表情")
                            for emoji, count in value.items():
                                if count > 0:
                                    print(f"    * {emoji}: {count}")
                        else:
                            print(f"  - {field}: {value}")
                
                # 計算總互動數
                total_interactions = (
                    interaction_data.raw_data.get("commentCount", 0) +
                    interaction_data.raw_data.get("interestedCount", 0) +
                    interaction_data.raw_data.get("collectedCount", 0)
                )
                
                emoji_count = interaction_data.raw_data.get("emojiCount", {})
                if isinstance(emoji_count, dict):
                    total_emojis = sum(emoji_count.values())
                    total_interactions += total_emojis
                
                print(f"\n📈 互動數據總結:")
                print(f"  - 總互動數: {total_interactions}")
                print(f"  - 留言數: {interaction_data.raw_data.get('commentCount', 0)}")
                print(f"  - 讚數: {interaction_data.raw_data.get('interestedCount', 0)}")
                print(f"  - 收藏數: {interaction_data.raw_data.get('collectedCount', 0)}")
                print(f"  - 表情數: {total_emojis if isinstance(emoji_count, dict) else 0}")
        
        return interaction_data
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        return None

async def test_multiple_articles():
    """測試多個文章 ID"""
    print("\n🔄 測試多個文章 ID...")
    print("=" * 60)
    
    # 初始化客戶端
    client = CMoneyClient()
    
    # 測試文章 ID 列表
    test_article_ids = [
        "173337593",  # 您提供的 ID
        "173337594",  # 相近的 ID
        "173337595",  # 相近的 ID
    ]
    
    # 登入憑證
    email = os.getenv("CMONEY_EMAIL", "test@example.com")
    password = os.getenv("CMONEY_PASSWORD", "test_password")
    credentials = LoginCredentials(email=email, password=password)
    
    try:
        # 登入
        access_token = await client.login(credentials)
        print(f"✅ 登入成功，開始測試多個文章...")
        
        results = []
        
        for i, article_id in enumerate(test_article_ids, 1):
            print(f"\n📝 測試 {i}/{len(test_article_ids)}: Article ID {article_id}")
            print("-" * 40)
            
            try:
                interaction_data = await client.get_article_interactions(access_token.token, article_id)
                
                if interaction_data.raw_data and "error" not in interaction_data.raw_data:
                    print(f"✅ 成功獲取數據:")
                    print(f"  - 讚數: {interaction_data.likes}")
                    print(f"  - 留言數: {interaction_data.comments}")
                    print(f"  - 總互動: {interaction_data.engagement_rate}")
                    results.append({"article_id": article_id, "success": True, "data": interaction_data})
                else:
                    error_msg = interaction_data.raw_data.get("error", "未知錯誤") if interaction_data.raw_data else "無數據"
                    print(f"❌ 失敗: {error_msg}")
                    results.append({"article_id": article_id, "success": False, "error": error_msg})
                    
            except Exception as e:
                print(f"❌ 測試失敗: {e}")
                results.append({"article_id": article_id, "success": False, "error": str(e)})
        
        return results
        
    except Exception as e:
        print(f"❌ 登入失敗: {e}")
        return []

async def main():
    """主函數"""
    print("🧪 CMoney API 完整測試工具")
    print("=" * 60)
    print(f"⏰ 測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 測試單個文章
    print("\n1️⃣ 測試單個文章 API")
    result = await test_cmoney_with_login()
    
    # 2. 測試多個文章
    print("\n2️⃣ 測試多個文章 ID")
    multiple_results = await test_multiple_articles()
    
    # 3. 總結
    print("\n📊 測試總結")
    print("=" * 60)
    
    if result and result.raw_data and "error" not in result.raw_data:
        print("✅ 單個文章測試成功")
        print(f"  - 文章 ID: {result.post_id}")
        print(f"  - 總互動數: {result.engagement_rate}")
    else:
        print("❌ 單個文章測試失敗")
    
    successful_tests = sum(1 for r in multiple_results if r["success"])
    total_tests = len(multiple_results)
    
    print(f"✅ 多個文章測試: {successful_tests}/{total_tests} 成功")
    
    if successful_tests > 0:
        print("\n🎯 可用於儀表板的數據:")
        print("- commentCount: 留言數")
        print("- interestedCount: 讚數") 
        print("- collectedCount: 收藏數")
        print("- emojiCount: 表情數據")
        print("- 總互動數: 所有互動數據的總和")
    
    print("\n✅ 測試完成！")

if __name__ == "__main__":
    asyncio.run(main())
