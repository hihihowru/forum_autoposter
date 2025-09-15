#!/usr/bin/env python3
"""
直接嘗試刪除文章 173691531
"""

import requests

def direct_delete():
    """直接刪除文章"""
    
    print("🗑️ 直接刪除文章 173691531")
    print("=" * 50)
    
    # 你提供的 Bearer token
    access_token = os.getenv('CMONEY_ACCESS_TOKEN')
    if not access_token:
        print("❌ 錯誤: 未設置 CMONEY_ACCESS_TOKEN 環境變數")
        return
    
    article_id = "173691531"
    delete_url = f"https://forumservice.cmoney.tw/api/Article/Delete/{article_id}"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "cmoneyapi-trace-context": '{"manufacturer":"Apple","appId":18,"model":"iPhone15,3","osName":"iOS","appVersion":"2.42.0","osVersion":"18.6.2","platform":1}',
        "Accept-Encoding": "gzip"
    }
    
    print(f"📡 URL: {delete_url}")
    print(f"🔑 Token: {access_token[:50]}...")
    
    try:
        print(f"\n🗑️ 發送 DELETE 請求...")
        
        response = requests.delete(delete_url, headers=headers)
        
        print(f"📊 狀態碼: {response.status_code}")
        print(f"📋 標頭: {dict(response.headers)}")
        
        if response.status_code == 204:
            print(f"🎉 成功刪除文章 {article_id}！")
            print("✅ 回應: 204 No Content (成功)")
            return True
        elif response.status_code == 404:
            print(f"⚠️ 文章 {article_id} 不存在")
            print("📝 可能原因:")
            print("   - 文章已經被刪除")
            print("   - 文章 ID 不正確")
            print("   - 文章不屬於這個用戶")
        elif response.status_code == 403:
            print(f"⚠️ 無權限刪除文章 {article_id}")
            print("📝 可能原因:")
            print("   - Token 過期")
            print("   - 用戶沒有刪除權限")
            print("   - 文章不屬於這個用戶")
        elif response.status_code == 401:
            print(f"⚠️ 認證失敗")
            print("📝 可能原因:")
            print("   - Token 無效")
            print("   - Token 格式錯誤")
        else:
            print(f"❌ 刪除失敗: {response.status_code}")
        
        print(f"\n📝 回應內容: {response.text}")
        
        return False
        
    except Exception as e:
        print(f"❌ 請求異常: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 直接刪除文章 173691531")
    
    success = direct_delete()
    
    print("\n" + "=" * 50)
    print("📊 刪除結果")
    print("=" * 50)
    
    if success:
        print("🎉 文章 173691531 已成功刪除！")
    else:
        print("❌ 刪除失敗或文章不存在")
        print("\n💡 建議:")
        print("   1. 檢查文章 ID 是否正確")
        print("   2. 確認文章是否還存在")
        print("   3. 檢查 token 是否有效")
        print("   4. 確認用戶是否有刪除權限")


