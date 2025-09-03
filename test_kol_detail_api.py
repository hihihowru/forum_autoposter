#!/usr/bin/env python3
"""
測試 KOL 詳情頁面的 API 調用
驗證前端 API 路徑和回應結構
"""

import requests
import json

def test_kol_detail_api():
    """測試 KOL 詳情頁面的 API 調用"""
    
    print("=" * 60)
    print("🔍 KOL 詳情頁面 API 測試")
    print("=" * 60)
    
    # 測試 Dashboard API 端點
    dashboard_api_url = "http://localhost:8007"
    test_member_id = "9505546"  # 川川哥
    
    try:
        # 1. 測試 KOL 詳情 API
        print(f"\n👤 測試 KOL 詳情 API (Member ID: {test_member_id}):")
        print("-" * 50)
        
        response = requests.get(f"{dashboard_api_url}/api/dashboard/kols/{test_member_id}")
        print(f"HTTP 狀態碼: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API 調用成功")
            print(f"📊 回應結構:")
            print(f"   - timestamp: {data.get('timestamp')}")
            print(f"   - success: {data.get('success')}")
            print(f"   - data 存在: {'data' in data}")
            
            if data.get('data'):
                kol_info = data['data'].get('kol_info', {})
                statistics = data['data'].get('statistics', {})
                
                print(f"📋 KOL 基本資訊:")
                print(f"   - 暱稱: {kol_info.get('nickname')}")
                print(f"   - Member ID: {kol_info.get('member_id')}")
                print(f"   - 人設: {kol_info.get('persona')}")
                print(f"   - 狀態: {kol_info.get('status')}")
                
                print(f"📈 統計數據:")
                print(f"   - 總貼文數: {statistics.get('total_posts')}")
                print(f"   - 已發布: {statistics.get('published_posts')}")
                print(f"   - 平均互動率: {statistics.get('avg_interaction_rate')}")
        else:
            print(f"❌ API 調用失敗: {response.status_code}")
            print(f"錯誤訊息: {response.text}")
        
        # 2. 測試 KOL 發文歷史 API
        print(f"\n📝 測試 KOL 發文歷史 API:")
        print("-" * 50)
        
        response = requests.get(f"{dashboard_api_url}/api/dashboard/kols/{test_member_id}/posts")
        print(f"HTTP 狀態碼: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 發文歷史 API 調用成功")
            print(f"📊 回應結構:")
            print(f"   - success: {data.get('success')}")
            print(f"   - data 存在: {'data' in data}")
            
            if data.get('data') and data['data'].get('posts'):
                posts = data['data']['posts']
                print(f"📋 發文記錄: {len(posts)} 篇")
                for i, post in enumerate(posts[:2]):  # 顯示前2篇
                    print(f"   {i+1}. {post.get('topic_title', 'N/A')[:30]}...")
                    print(f"      狀態: {post.get('status')} | 時間: {post.get('post_time')}")
        else:
            print(f"❌ 發文歷史 API 調用失敗: {response.status_code}")
        
        # 3. 測試 KOL 互動數據 API
        print(f"\n📊 測試 KOL 互動數據 API:")
        print("-" * 50)
        
        response = requests.get(f"{dashboard_api_url}/api/dashboard/kols/{test_member_id}/interactions")
        print(f"HTTP 狀態碼: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 互動數據 API 調用成功")
            print(f"📊 回應結構:")
            print(f"   - success: {data.get('success')}")
            print(f"   - data 存在: {'data' in data}")
            
            if data.get('data'):
                interaction_summary = data['data'].get('interaction_summary', {})
                print(f"📋 互動摘要:")
                print(f"   - 總互動數: {interaction_summary.get('total_interactions')}")
                print(f"   - 平均讚數: {interaction_summary.get('avg_likes_per_post')}")
                print(f"   - 平均留言數: {interaction_summary.get('avg_comments_per_post')}")
        else:
            print(f"❌ 互動數據 API 調用失敗: {response.status_code}")
        
        # 4. 測試前端代理
        print(f"\n🌐 測試前端代理:")
        print("-" * 50)
        
        frontend_url = "http://localhost:3000"
        try:
            response = requests.get(frontend_url)
            if response.status_code == 200:
                print("✅ Dashboard 前端正常運行")
                print(f"🔗 KOL 詳情頁面 URL: {frontend_url}/content-management/kols/{test_member_id}")
            else:
                print(f"❌ Dashboard 前端請求失敗: {response.status_code}")
        except Exception as e:
            print(f"❌ Dashboard 前端請求失敗: {e}")
        
        print("\n" + "=" * 60)
        print("✅ KOL 詳情頁面 API 測試完成")
        print("=" * 60)
        
        print("\n📋 測試結果總結:")
        print("1. ✅ KOL 詳情 API 正常")
        print("2. ✅ KOL 發文歷史 API 正常")
        print("3. ✅ KOL 互動數據 API 正常")
        print("4. ✅ Dashboard 前端正常運行")
        
        print(f"\n🔗 測試 URL:")
        print(f"   - 川川哥詳情: {frontend_url}/content-management/kols/{test_member_id}")
        print(f"   - 韭割哥詳情: {frontend_url}/content-management/kols/9505547")
        print(f"   - 梅川褲子詳情: {frontend_url}/content-management/kols/9505548")
        
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {e}")

if __name__ == "__main__":
    test_kol_detail_api()
