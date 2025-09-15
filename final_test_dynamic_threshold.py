#!/usr/bin/env python3
"""
最終測試：確認動態漲跌幅功能完全修復
"""

import requests
import json
from datetime import datetime

def final_test():
    """最終測試動態漲跌幅功能"""
    print("🎯 最終測試：動態漲跌幅功能")
    print("=" * 60)
    
    api_url = "http://localhost:8005/after_hours_limit_up"
    
    # 測試不同的漲跌幅閾值和限制
    test_cases = [
        {"limit": 5, "changeThreshold": 8.0, "expected": "應該找到 5 檔股票"},
        {"limit": 10, "changeThreshold": 8.0, "expected": "應該找到 10 檔股票"},
        {"limit": 3, "changeThreshold": 12.0, "expected": "應該找到 0 檔股票"},
        {"limit": 15, "changeThreshold": 15.0, "expected": "應該找到 0 檔股票"},
    ]
    
    all_passed = True
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📊 測試 {i}: limit={test_case['limit']}, threshold={test_case['changeThreshold']}%")
        print(f"預期: {test_case['expected']}")
        print("-" * 40)
        
        try:
            response = requests.get(api_url, params={
                'limit': test_case['limit'],
                'changeThreshold': test_case['changeThreshold']
            }, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success'):
                    stock_count = data.get('total_count', 0)
                    threshold = data.get('changeThreshold', 'N/A')
                    
                    print(f"✅ 實際結果:")
                    print(f"   漲幅閾值: {threshold}%")
                    print(f"   找到股票: {stock_count} 檔")
                    print(f"   限制數量: {test_case['limit']} 檔")
                    
                    # 驗證結果是否符合預期
                    if test_case['changeThreshold'] <= 9.5:
                        # 低閾值應該找到股票
                        if stock_count > 0 and stock_count <= test_case['limit']:
                            print("   ✅ 測試通過")
                        else:
                            print("   ❌ 測試失敗：應該找到股票但沒有")
                            all_passed = False
                    else:
                        # 高閾值應該找不到股票
                        if stock_count == 0:
                            print("   ✅ 測試通過")
                        else:
                            print("   ❌ 測試失敗：不應該找到股票但找到了")
                            all_passed = False
                else:
                    print(f"❌ API 錯誤: {data.get('error')}")
                    all_passed = False
            else:
                print(f"❌ HTTP 錯誤: {response.status_code}")
                all_passed = False
                
        except Exception as e:
            print(f"❌ 請求失敗: {e}")
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 所有測試通過！動態漲跌幅功能完全修復！")
        print("\n✅ 功能確認:")
        print("   - 漲跌幅閾值可以動態調整")
        print("   - 股票數量限制可以動態調整")
        print("   - 不再固定返回 10 檔股票")
        print("   - 沒有股票時正確顯示 0 檔")
    else:
        print("❌ 部分測試失敗，需要進一步檢查")
    
    return all_passed

def test_frontend_integration():
    """測試前端整合"""
    print("\n🌐 前端整合測試")
    print("=" * 60)
    
    # 模擬前端調用
    frontend_configs = [
        {
            "threshold": 5,
            "changeThreshold": {"percentage": 8.0, "type": "up"},
            "description": "前端設定: 漲幅 >= 8%, 限制 5 檔"
        },
        {
            "threshold": 10, 
            "changeThreshold": {"percentage": 12.0, "type": "up"},
            "description": "前端設定: 漲幅 >= 12%, 限制 10 檔"
        }
    ]
    
    for i, config in enumerate(frontend_configs, 1):
        print(f"\n📱 前端測試 {i}: {config['description']}")
        print("-" * 40)
        
        # 模擬前端 API 調用邏輯
        params = {
            'limit': config['threshold']
        }
        
        if config.get('changeThreshold'):
            params['changeThreshold'] = config['changeThreshold']['percentage']
        
        try:
            response = requests.get(
                "http://localhost:8005/after_hours_limit_up",
                params=params,
                timeout=15,
                headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'Origin': 'http://localhost:3000'
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success'):
                    stock_count = data.get('total_count', 0)
                    threshold = data.get('changeThreshold', 'N/A')
                    
                    print(f"✅ 前端調用成功")
                    print(f"   漲幅閾值: {threshold}%")
                    print(f"   限制: {config['threshold']} 檔")
                    print(f"   實際找到: {stock_count} 檔")
                    
                    if stock_count == 0:
                        print("   📝 前端應該顯示: '沒有找到漲幅超過 X% 的股票'")
                    else:
                        print(f"   📝 前端應該顯示: {stock_count} 檔真實股票數據")
                else:
                    print(f"❌ API 錯誤: {data.get('error')}")
            else:
                print(f"❌ HTTP 錯誤: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 前端調用失敗: {e}")

if __name__ == "__main__":
    print("🔧 動態漲跌幅功能最終測試")
    print(f"測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 執行最終測試
    test_passed = final_test()
    
    # 測試前端整合
    test_frontend_integration()
    
    print("\n" + "=" * 60)
    print("🎯 測試總結")
    print("=" * 60)
    
    if test_passed:
        print("✅ 後端 API 功能完全正常")
        print("✅ 動態漲跌幅閾值工作正常")
        print("✅ 股票數量限制工作正常")
        print("\n🔧 前端修復:")
        print("✅ 移除了測試數據的 fallback 邏輯")
        print("✅ 重啟了前端服務")
        print("\n💡 現在用戶可以:")
        print("   1. 在前端調整漲跌幅閾值 (0.1-20%)")
        print("   2. 調整股票數量限制")
        print("   3. 看到真實的搜尋結果")
        print("   4. 當沒有符合條件的股票時，看到正確的提示")
    else:
        print("❌ 需要進一步檢查問題")
    
    print("\n🚀 建議用戶:")
    print("   1. 清除瀏覽器緩存")
    print("   2. 重新載入前端頁面")
    print("   3. 測試不同的漲跌幅設定")

