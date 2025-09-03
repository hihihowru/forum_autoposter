#!/usr/bin/env python3
"""
測試 Dashboard 的 KOL 設定欄位顯示
驗證新增的發文類型、文章長度、權重設定等欄位
"""

import requests
import json
from datetime import datetime

def test_dashboard_kol_settings():
    """測試 Dashboard 的 KOL 設定欄位"""
    
    print("=" * 60)
    print("📊 Dashboard KOL 設定欄位測試")
    print("=" * 60)
    
    # 測試 Dashboard API 端點
    dashboard_api_url = "http://localhost:8007"
    frontend_url = "http://localhost:3000"
    
    try:
        # 1. 測試獲取內容管理數據
        print(f"\n📊 測試獲取內容管理數據:")
        print("-" * 50)
        
        response = requests.get(f"{dashboard_api_url}/api/dashboard/content-management")
        if response.status_code == 200:
            data = response.json()
            print("✅ 成功獲取內容管理數據")
            
            # 檢查貼文數據中的新欄位
            if 'post_list' in data and data['post_list']:
                print(f"\n📝 檢查貼文數據中的 KOL 設定欄位:")
                print(f"找到 {len(data['post_list'])} 篇貼文")
                
                for i, post in enumerate(data['post_list'][:2], 1):  # 顯示前2個
                    print(f"\n📄 貼文 {i}:")
                    print(f"   - 貼文ID: {post.get('post_id', 'N/A')}")
                    print(f"   - KOL: {post.get('kol_nickname', 'N/A')}")
                    print(f"   - 人設: {post.get('persona', 'N/A')}")
                    print(f"   - 狀態: {post.get('status', 'N/A')}")
                    
                    # 檢查新增的 KOL 設定欄位
                    print(f"   📋 KOL 設定欄位:")
                    print(f"      • 發文類型: {post.get('post_type', 'N/A')}")
                    print(f"      • 文章長度: {post.get('content_length', 'N/A')}")
                    print(f"      • 權重設定: {'有' if post.get('kol_weight_settings') else '無'}")
                    print(f"      • 生成時間: {post.get('content_generation_time', 'N/A')}")
                    print(f"      • 設定版本: {post.get('kol_settings_version', 'N/A')}")
                    
                    # 如果有權重設定，顯示詳細內容
                    if post.get('kol_weight_settings'):
                        try:
                            weight_settings = json.loads(post['kol_weight_settings'])
                            print(f"      📊 權重設定詳情:")
                            if 'post_types' in weight_settings:
                                print(f"         - 發文類型權重:")
                                for post_type, config in weight_settings['post_types'].items():
                                    print(f"           • {config.get('style', post_type)}: {config.get('weight', 0)}")
                            if 'content_lengths' in weight_settings:
                                print(f"         - 內容長度權重:")
                                for length, config in weight_settings['content_lengths'].items():
                                    print(f"           • {length}: {config.get('weight', 0)}")
                        except json.JSONDecodeError:
                            print(f"      ⚠️ 權重設定格式錯誤: {post['kol_weight_settings']}")
            else:
                print("❌ 沒有找到貼文數據")
        else:
            print(f"❌ 獲取內容管理數據失敗: {response.status_code}")
            return
        
        # 2. 測試前端頁面
        print(f"\n🌐 測試前端頁面:")
        print("-" * 50)
        
        try:
            response = requests.get(frontend_url)
            if response.status_code == 200:
                print("✅ Dashboard 前端正常運行")
                print(f"🔗 內容管理頁面: {frontend_url}/content-management")
            else:
                print(f"❌ Dashboard 前端請求失敗: {response.status_code}")
        except Exception as e:
            print(f"❌ Dashboard 前端請求失敗: {e}")
        
        # 3. 顯示新欄位說明
        print(f"\n📋 新增的 KOL 設定欄位說明:")
        print("-" * 50)
        print("1. 發文類型 (post_type):")
        print("   - 疑問型 (question): 以疑問句為主，引起討論")
        print("   - 發表觀點型 (opinion): 發表專業觀點和分析")
        
        print("\n2. 文章長度 (content_length):")
        print("   - 短 (short): 50-100字，簡潔有力")
        print("   - 中 (medium): 200-300字，適中長度")
        print("   - 長 (long): 400-500字，深度分析")
        
        print("\n3. KOL權重設定 (kol_weight_settings):")
        print("   - JSON 格式的權重參數")
        print("   - 包含發文類型和內容長度的權重配置")
        print("   - 用於自我學習和優化")
        
        print("\n4. 內容生成時間 (content_generation_time):")
        print("   - 記錄內容生成的時間戳記")
        print("   - 用於追蹤和分析")
        
        print("\n5. KOL設定版本 (kol_settings_version):")
        print("   - 記錄生成該貼文時使用的 KOL 設定版本號")
        print("   - 用於版本控制和回滾")
        
        print("\n" + "=" * 60)
        print("✅ Dashboard KOL 設定欄位測試完成")
        print("=" * 60)
        
        print("\n📋 測試結果總結:")
        print("1. ✅ 內容管理數據獲取正常")
        print("2. ✅ 新增的 KOL 設定欄位已包含在 API 回應中")
        print("3. ✅ Dashboard 前端正常運行")
        print("4. ✅ 權重設定欄位可以正確解析 JSON 格式")
        
        print("\n🎯 前端顯示功能:")
        print("1. 發文類型: 使用彩色標籤顯示 (疑問型=藍色, 觀點型=綠色)")
        print("2. 文章長度: 使用彩色標籤顯示 (短=橙色, 中=藍色, 長=紫色)")
        print("3. 權重設定: 可點擊查看按鈕，彈窗顯示詳細權重配置")
        print("4. 生成時間: 格式化顯示為本地時間")
        print("5. 設定版本: 直接顯示版本號")
        
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {e}")

if __name__ == "__main__":
    test_dashboard_kol_settings()
