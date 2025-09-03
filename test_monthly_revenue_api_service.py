#!/usr/bin/env python3
"""
測試月營收 API 服務
"""

import requests
import json
import time

def test_monthly_revenue_api():
    """測試月營收API服務"""
    
    base_url = "http://localhost:8002"
    
    print("🚀 測試月營收 API 服務")
    print("=" * 50)
    
    # 等待服務啟動
    print("⏳ 等待服務啟動...")
    time.sleep(2)
    
    try:
        # 1. 測試根路徑
        print("\n🔍 測試根路徑...")
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ 根路徑測試成功")
            print(f"   API 版本: {response.json().get('version')}")
        else:
            print(f"❌ 根路徑測試失敗: {response.status_code}")
            return False
        
        # 2. 測試健康檢查
        print("\n🔍 測試健康檢查...")
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ 健康檢查測試成功")
            print(f"   狀態: {response.json().get('status')}")
        else:
            print(f"❌ 健康檢查測試失敗: {response.status_code}")
            return False
        
        # 3. 測試獲取台積電月營收數據
        print("\n🔍 測試獲取台積電月營收數據...")
        response = requests.get(f"{base_url}/monthly_revenue/2330")
        if response.status_code == 200:
            data = response.json()
            print("✅ 台積電月營收數據獲取成功")
            print(f"   股票代號: {data.get('stock_id')}")
            print(f"   數據筆數: {len(data.get('data', []))}")
            
            if data.get('data'):
                latest = data['data'][-1]
                print(f"   最新月份: {latest.get('月份')}")
                print(f"   當月營收: {latest.get('當月營收')} 百萬元")
                print(f"   年增率: {latest.get('去年同月增減(%)')}%")
        else:
            print(f"❌ 台積電月營收數據獲取失敗: {response.status_code}")
            return False
        
        # 4. 測試獲取台積電營收摘要
        print("\n🔍 測試獲取台積電營收摘要...")
        response = requests.get(f"{base_url}/revenue_summary/2330")
        if response.status_code == 200:
            data = response.json()
            print("✅ 台積電營收摘要獲取成功")
            print(f"   最新月份: {data.get('最新月份')}")
            print(f"   年增率: {data.get('年增率')}")
            print(f"   月增率: {data.get('月增率')}")
            print(f"   營收趨勢: {data.get('營收趨勢')}")
            print(f"   投資建議: {data.get('投資建議')}")
        else:
            print(f"❌ 台積電營收摘要獲取失敗: {response.status_code}")
            return False
        
        # 5. 測試獲取營收表現最佳股票
        print("\n🔍 測試獲取營收表現最佳股票...")
        response = requests.get(f"{base_url}/top_performers?metric=去年同月增減(%)&top_n=3")
        if response.status_code == 200:
            data = response.json()
            print("✅ 營收表現最佳股票獲取成功")
            print(f"   返回股票數量: {len(data)}")
            
            for i, stock in enumerate(data):
                print(f"   {i+1}. {stock.get('stock_id')} - 年增率: {stock.get('去年同月增減(%)')}%")
        else:
            print(f"❌ 營收表現最佳股票獲取失敗: {response.status_code}")
            return False
        
        # 6. 測試不同指標的排序
        print("\n🔍 測試不同指標排序...")
        metrics = ["上月比較增減(%)", "當月營收"]
        
        for metric in metrics:
            response = requests.get(f"{base_url}/top_performers?metric={metric}&top_n=2")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {metric} 排序成功")
                for stock in data:
                    print(f"   {stock.get('stock_id')}: {stock.get(metric)}")
            else:
                print(f"❌ {metric} 排序失敗: {response.status_code}")
        
        # 7. 測試錯誤處理
        print("\n🔍 測試錯誤處理...")
        
        # 測試不存在的股票
        response = requests.get(f"{base_url}/monthly_revenue/9999")
        if response.status_code == 404:
            print("✅ 不存在的股票錯誤處理正確")
        else:
            print(f"❌ 不存在的股票錯誤處理異常: {response.status_code}")
        
        # 測試無效的排序指標
        response = requests.get(f"{base_url}/top_performers?metric=無效指標")
        if response.status_code == 400:
            print("✅ 無效指標錯誤處理正確")
        else:
            print(f"❌ 無效指標錯誤處理異常: {response.status_code}")
        
        print("\n🎉 所有測試完成！")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ 無法連接到API服務，請確保服務已啟動")
        return False
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {e}")
        return False

if __name__ == "__main__":
    success = test_monthly_revenue_api()
    
    if success:
        print("\n✅ 月營收API服務測試全部通過！")
        print("服務運行正常，可以開始使用")
    else:
        print("\n❌ 月營收API服務測試失敗")
        print("請檢查服務狀態和錯誤訊息")



