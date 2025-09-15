#!/usr/bin/env python3
"""
直接使用 Bearer token 刪除 CMoney 文章 173691531
"""

import requests

def delete_article_with_token():
    """使用提供的 Bearer token 刪除文章"""
    
    print("🗑️ 使用 Bearer token 刪除文章 173691531")
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
    
    print(f"📡 刪除 URL: {delete_url}")
    print(f"🔑 Authorization: Bearer {access_token[:50]}...")
    print(f"📋 Headers: {headers}")
    
    try:
        print(f"\n🗑️ 開始刪除文章 {article_id}...")
        
        response = requests.delete(delete_url, headers=headers)
        
        print(f"📊 回應狀態碼: {response.status_code}")
        print(f"📋 回應標頭: {dict(response.headers)}")
        
        if response.status_code == 204:
            print(f"🎉 成功刪除文章 {article_id}！")
            return True
        else:
            print(f"❌ 刪除失敗: {response.status_code}")
            print(f"📝 回應內容: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 刪除異常: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 直接使用 Bearer token 刪除文章")
    
    success = delete_article_with_token()
    
    print("\n" + "=" * 50)
    print("📊 刪除結果")
    print("=" * 50)
    
    if success:
        print("🎉 文章 173691531 已成功刪除！")
    else:
        print("❌ 刪除失敗")


