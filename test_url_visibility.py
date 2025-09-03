#!/usr/bin/env python3
"""
測試 URL 連結的可見性
檢查 KOL 管理和貼文管理頁面的 URL 連結是否正確顯示
"""

import requests
import json
from datetime import datetime

def test_url_visibility():
    """測試 URL 連結的可見性"""
    
    print("=" * 60)
    print("🔗 URL 連結可見性測試")
    print("=" * 60)
    
    # 測試 Dashboard API 端點
    dashboard_api_url = "http://localhost:8007"
    
    try:
        # 1. 測試獲取內容管理數據
        print(f"\n📊 測試獲取內容管理數據:")
        print("-" * 50)
        
        response = requests.get(f"{dashboard_api_url}/api/dashboard/content-management")
        if response.status_code == 200:
            data = response.json()
            print("✅ 成功獲取內容管理數據")
            
            # 檢查 KOL 數據
            if 'kol_list' in data and data['kol_list']:
                print(f"\n👤 KOL 管理表格 URL 連結:")
                print(f"找到 {len(data['kol_list'])} 個 KOL")
                
                for i, kol in enumerate(data['kol_list'][:3], 1):  # 顯示前3個
                    member_id = kol.get('member_id')
                    nickname = kol.get('nickname')
                    print(f"   {i}. {nickname} (ID: {member_id})")
                    print(f"      🔗 會員主頁連結: https://www.cmoney.tw/forum/user/{member_id}")
                    print(f"      📍 在 KOL 管理表格的 Member ID 欄位旁邊應該有 🔗 圖示")
            
            # 檢查貼文數據
            if 'post_list' in data and data['post_list']:
                print(f"\n📝 貼文管理表格 URL 連結:")
                print(f"找到 {len(data['post_list'])} 篇貼文")
                
                for i, post in enumerate(data['post_list'][:3], 1):  # 顯示前3個
                    post_id = post.get('post_id')
                    article_id = post.get('platform_post_id')
                    kol_nickname = post.get('kol_nickname')
                    status = post.get('status')
                    print(f"   {i}. {post_id} ({kol_nickname}) - {status}")
                    
                    if article_id:
                        print(f"      🔗 文章連結: https://www.cmoney.tw/forum/article/{article_id}")
                        print(f"      📍 在貼文管理表格的貼文 ID 欄位旁邊應該有 🔗 圖示")
                    else:
                        print(f"      ⚠️ 尚未發布，無文章連結")
                        print(f"      📍 只有已發布的貼文才會顯示 🔗 圖示")
        else:
            print(f"❌ 獲取內容管理數據失敗: {response.status_code}")
            return
        
        # 2. 顯示 URL 連結使用說明
        print(f"\n📋 URL 連結使用說明:")
        print("-" * 50)
        print("🔗 KOL 管理頁面:")
        print("   - 位置: http://localhost:3001/content-management")
        print("   - 切換到「KOL 管理」標籤")
        print("   - 在「Member ID」欄位旁邊有 🔗 圖示")
        print("   - 點擊可跳轉到該 KOL 的同學會會員主頁")
        print("   - 格式: https://www.cmoney.tw/forum/user/{member_id}")
        
        print("\n🔗 貼文管理頁面:")
        print("   - 位置: http://localhost:3001/content-management")
        print("   - 切換到「貼文管理」標籤")
        print("   - 在「貼文 ID」欄位旁邊有 🔗 圖示")
        print("   - 點擊可跳轉到該文章的詳細頁面")
        print("   - 格式: https://www.cmoney.tw/forum/article/{article_id}")
        print("   - 只有已發布的貼文才有連結")
        
        print("\n🎯 如何查看 URL 連結:")
        print("1. 打開 http://localhost:3000/content-management")
        print("2. 在 KOL 管理標籤中，查看 Member ID 欄位")
        print("3. 在貼文管理標籤中，查看貼文 ID 欄位")
        print("4. 尋找 🔗 圖示（ExternalLinkOutlined 圖標）")
        print("5. 點擊圖示會在新分頁中打開對應的同學會頁面")
        
        print("\n⚠️ 如果看不到 🔗 圖示:")
        print("1. 檢查瀏覽器是否支援圖標字體")
        print("2. 確認 Ant Design 圖標庫已正確載入")
        print("3. 檢查瀏覽器開發者工具是否有 JavaScript 錯誤")
        print("4. 嘗試重新整理頁面")
        
        print("\n" + "=" * 60)
        print("✅ URL 連結可見性測試完成")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {e}")

if __name__ == "__main__":
    test_url_visibility()
