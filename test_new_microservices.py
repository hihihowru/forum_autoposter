#!/usr/bin/env python3
"""
測試新建立的微服務
"""

import requests
import json
import time

# API 端點配置
BASE_URLS = {
    "revenue": "http://localhost:8008",
    "financial": "http://localhost:8009",
    "fundamental": "http://localhost:8010"
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

def test_revenue_api():
    """測試營收 API"""
    print("\n📊 測試營收 API...")
    
    try:
        # 測試營收摘要
        response = requests.get(f"{BASE_URLS['revenue']}/revenue/2330/summary")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 營收摘要: {data['stock_id']}")
            print(f"   當月營收: {data['current_revenue']['formatted']}")
            print(f"   年增率: {data['growth']['year_over_year']}%")
            print(f"   趨勢: {data['trend']}")
        else:
            print(f"❌ 營收摘要失敗: {response.status_code}")
        
        # 測試成長率資料
        response = requests.get(f"{BASE_URLS['revenue']}/revenue/2330/growth?periods=3")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 成長率資料: 取得 {len(data['growth_data'])} 期資料")
        else:
            print(f"❌ 成長率資料失敗: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 營收 API 測試失敗: {e}")

def test_financial_api():
    """測試財報 API"""
    print("\n📈 測試財報 API...")
    
    try:
        # 測試財務摘要
        response = requests.get(f"{BASE_URLS['financial']}/financial/2330/summary")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 財務摘要: {data['stock_id']}")
            print(f"   營業利益: {data['profitability']['operating_profit']['formatted']}")
            print(f"   營業利益率: {data['profitability']['operating_margin']}%")
            print(f"   ROE: {data['profitability']['roe']}%")
            print(f"   財務健康度: {data['analysis']['overall_health']}")
        else:
            print(f"❌ 財務摘要失敗: {response.status_code}")
        
        # 測試財務比率
        response = requests.get(f"{BASE_URLS['financial']}/financial/2330/ratios?periods=2")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 財務比率: 取得 {len(data['ratios_data'])} 期資料")
        else:
            print(f"❌ 財務比率失敗: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 財報 API 測試失敗: {e}")

def test_fundamental_analyzer():
    """測試基本面分析器"""
    print("\n🔍 測試基本面分析器...")
    
    try:
        # 測試基本面分析
        response = requests.post(f"{BASE_URLS['fundamental']}/analyze/fundamental?stock_id=2330")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 基本面分析: {data['stock_id']}")
            print(f"   產業: {data['kol_insights']['industry']['industry']}")
            print(f"   標題: {data['kol_insights']['insight_title']}")
            print(f"   關鍵洞察: {len(data['kol_insights']['key_insights'])} 個")
        else:
            print(f"❌ 基本面分析失敗: {response.status_code}")
        
        # 測試 KOL 內容生成
        response = requests.post(f"{BASE_URLS['fundamental']}/generate/kol-content?stock_id=2330&content_style=analysis")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ KOL 內容生成: {data['content_style']}")
            print(f"   標題: {data['title']}")
            print(f"   關鍵點: {len(data['key_points'])} 個")
        else:
            print(f"❌ KOL 內容生成失敗: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 基本面分析器測試失敗: {e}")

def test_multiple_stocks():
    """測試多檔股票"""
    print("\n📋 測試多檔股票...")
    
    test_stocks = ['2330', '2317', '2454']
    
    for stock_id in test_stocks:
        try:
            print(f"\n測試股票: {stock_id}")
            
            # 營收摘要
            response = requests.get(f"{BASE_URLS['revenue']}/revenue/{stock_id}/summary")
            if response.status_code == 200:
                data = response.json()
                print(f"   營收: {data['current_revenue']['formatted']} (年增 {data['growth']['year_over_year']}%)")
            
            # 財務摘要
            response = requests.get(f"{BASE_URLS['financial']}/financial/{stock_id}/summary")
            if response.status_code == 200:
                data = response.json()
                print(f"   營業利益率: {data['profitability']['operating_margin']}%")
                print(f"   ROE: {data['profitability']['roe']}%")
                
        except Exception as e:
            print(f"   測試失敗: {e}")

if __name__ == "__main__":
    print("🚀 開始測試新建立的微服務...")
    
    # 等待服務啟動
    print("⏳ 等待服務啟動...")
    time.sleep(5)
    
    # 測試各項功能
    test_api_health()
    test_revenue_api()
    test_financial_api()
    test_fundamental_analyzer()
    test_multiple_stocks()
    
    print("\n✅ 測試完成")


