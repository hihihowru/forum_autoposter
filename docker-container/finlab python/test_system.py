#!/usr/bin/env python3
"""
虛擬KOL系統測試腳本
測試所有API端點和發文功能
"""

import requests
import json
import time
from datetime import datetime

# API 端點配置
BASE_URLS = {
    "ohlc": "http://localhost:8001",
    "analyze": "http://localhost:8002", 
    "summary": "http://localhost:8003",
    "trending": "http://localhost:8005",
    "posting": "http://localhost:8006"
}

def test_api_health():
    """測試所有API的健康狀態"""
    print("🏥 測試API健康狀態...")
    
    for service, url in BASE_URLS.items():
        try:
            response = requests.get(f"{url}/health", timeout=10)
            if response.status_code == 200:
                print(f"✅ {service}: 健康")
            else:
                print(f"❌ {service}: 異常 ({response.status_code})")
        except Exception as e:
            print(f"❌ {service}: 無法連接 - {e}")

def test_trending_api():
    """測試Trending API"""
    print("\n🔥 測試Trending API...")
    
    try:
        # 測試熱門話題
        response = requests.get(f"{BASE_URLS['trending']}/trending", params={"limit": 3})
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 熱門話題: 找到 {data.get('total_count', 0)} 個話題")
            for topic in data.get('topics', [])[:2]:
                print(f"   📌 {topic.get('title', 'N/A')}")
        else:
            print(f"❌ 熱門話題API失敗: {response.status_code}")
        
        # 測試熱門股票
        response = requests.get(f"{BASE_URLS['trending']}/trending/stocks", params={"limit": 5})
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 熱門股票: 找到 {data.get('total_count', 0)} 支股票")
            for stock in data.get('stocks', [])[:3]:
                print(f"   📈 {stock.get('stock_id', 'N/A')} - {stock.get('name', 'N/A')}")
        else:
            print(f"❌ 熱門股票API失敗: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Trending API測試失敗: {e}")

def test_content_generation():
    """測試內容生成"""
    print("\n📝 測試內容生成...")
    
    try:
        # 測試KOL內容生成
        content_request = {
            "stock_id": "2330",
            "kol_persona": "technical",
            "content_style": "chart_analysis",
            "target_audience": "active_traders"
        }
        
        response = requests.post(f"{BASE_URLS['summary']}/generate-kol-content", 
                               json=content_request, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ KOL內容生成成功")
            print(f"   👤 KOL: {data.get('kol_name', 'N/A')}")
            print(f"   📊 股票: {data.get('stock_id', 'N/A')}")
            print(f"   📝 標題: {data.get('title', 'N/A')}")
            print(f"   🔑 關鍵點: {', '.join(data.get('key_points', [])[:3])}")
        else:
            print(f"❌ 內容生成失敗: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 內容生成測試失敗: {e}")

def test_auto_posting():
    """測試自動發文功能"""
    print("\n🚀 測試自動發文功能...")
    
    try:
        # 測試自動發文
        config = {
            "enabled": True,
            "interval_minutes": 60,
            "max_posts_per_day": 10,
            "kol_personas": ["technical"]
        }
        
        response = requests.post(f"{BASE_URLS['posting']}/post/auto", 
                               json=config, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ 自動發文成功")
                print(f"   🆔 發文ID: {data.get('post_id', 'N/A')}")
                print(f"   📊 股票: {data.get('content', {}).get('stock_id', 'N/A')}")
                print(f"   👤 KOL: {data.get('content', {}).get('kol_name', 'N/A')}")
            else:
                print(f"❌ 自動發文失敗: {data.get('error', '未知錯誤')}")
        else:
            print(f"❌ 自動發文API失敗: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 自動發文測試失敗: {e}")

def test_manual_posting():
    """測試手動發文功能"""
    print("\n✋ 測試手動發文功能...")
    
    try:
        # 測試手動發文
        request = {
            "kol_persona": "fundamental",
            "content_style": "earnings_review",
            "target_audience": "long_term_investors",
            "auto_post": False
        }
        
        response = requests.post(f"{BASE_URLS['posting']}/post/manual", 
                               json=request, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ 手動發文成功")
                print(f"   🆔 發文ID: {data.get('post_id', 'N/A')}")
                print(f"   📊 股票: {data.get('content', {}).get('stock_id', 'N/A')}")
                print(f"   👤 KOL: {data.get('content', {}).get('kol_name', 'N/A')}")
            else:
                print(f"❌ 手動發文失敗: {data.get('error', '未知錯誤')}")
        else:
            print(f"❌ 手動發文API失敗: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 手動發文測試失敗: {e}")

def test_trending_preview():
    """測試熱門內容預覽"""
    print("\n👀 測試熱門內容預覽...")
    
    try:
        response = requests.get(f"{BASE_URLS['posting']}/trending/preview", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 熱門內容預覽成功")
            print(f"   📌 話題數量: {len(data.get('topics', []))}")
            print(f"   📈 股票數量: {len(data.get('stocks', []))}")
            
            # 顯示第一個話題
            if data.get('topics'):
                topic = data['topics'][0]
                print(f"   🔥 熱門話題: {topic.get('title', 'N/A')}")
                
            # 顯示第一支股票
            if data.get('stocks'):
                stock = data['stocks'][0]
                print(f"   📊 熱門股票: {stock.get('stock_id', 'N/A')} - {stock.get('name', 'N/A')}")
        else:
            print(f"❌ 熱門內容預覽失敗: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 熱門內容預覽測試失敗: {e}")

def main():
    """主測試函數"""
    print("🚀 虛擬KOL系統測試開始")
    print("=" * 50)
    print(f"⏰ 測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 等待服務啟動
    print("\n⏳ 等待服務啟動...")
    time.sleep(5)
    
    # 執行測試
    test_api_health()
    test_trending_api()
    test_content_generation()
    test_auto_posting()
    test_manual_posting()
    test_trending_preview()
    
    print("\n" + "=" * 50)
    print("🎉 測試完成！")
    print("\n📋 下一步:")
    print("1. 檢查所有API是否正常運作")
    print("2. 測試發文功能")
    print("3. 整合實際的發文平台API")
    print("4. 開始自動發文！")

if __name__ == "__main__":
    main()

