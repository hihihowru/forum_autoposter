"""
測試互動分析API是否正常工作
"""

import requests
import json

def test_interaction_api():
    """測試互動分析API"""
    
    print("🧪 測試互動分析API")
    print("=" * 50)
    
    # API端點
    api_url = "http://localhost:8007/api/dashboard/interaction-analysis"
    
    try:
        print(f"📝 測試API端點: {api_url}")
        
        # 發送GET請求
        response = requests.get(api_url, timeout=10)
        
        print(f"📊 響應狀態碼: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ API請求成功")
            
            try:
                data = response.json()
                print(f"📄 響應數據類型: {type(data)}")
                
                if isinstance(data, dict):
                    print(f"📋 響應數據鍵: {list(data.keys())}")
                    
                    # 檢查必要的欄位
                    required_fields = ['timestamp', 'interaction_data', 'statistics', 'data_source']
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if missing_fields:
                        print(f"⚠️ 缺少必要欄位: {missing_fields}")
                    else:
                        print("✅ 所有必要欄位都存在")
                    
                    # 檢查互動數據
                    if 'interaction_data' in data:
                        interaction_data = data['interaction_data']
                        print(f"📊 互動數據表格: {list(interaction_data.keys())}")
                        
                        for table_name, table_data in interaction_data.items():
                            print(f"  - {table_name}: {len(table_data)} 條記錄")
                    
                    # 檢查統計數據
                    if 'statistics' in data:
                        statistics = data['statistics']
                        print(f"📈 統計數據表格: {list(statistics.keys())}")
                        
                        for table_name, stats in statistics.items():
                            print(f"  - {table_name}:")
                            print(f"    總貼文數: {stats.get('total_posts', 0)}")
                            print(f"    總互動數: {stats.get('total_interactions', 0)}")
                            print(f"    總讚數: {stats.get('total_likes', 0)}")
                            print(f"    總留言數: {stats.get('total_comments', 0)}")
                
            except json.JSONDecodeError as e:
                print(f"❌ JSON解析失敗: {e}")
                print(f"原始響應: {response.text[:200]}...")
        
        elif response.status_code == 500:
            print("❌ 服務器內部錯誤")
            try:
                error_data = response.json()
                print(f"錯誤詳情: {error_data}")
            except:
                print(f"錯誤響應: {response.text}")
        
        else:
            print(f"❌ API請求失敗: {response.status_code}")
            print(f"響應內容: {response.text}")
    
    except requests.exceptions.ConnectionError:
        print("❌ 連接失敗 - 請確認API服務是否正在運行")
        print("💡 提示: 請檢查dashboard-api服務是否在localhost:8007上運行")
    
    except requests.exceptions.Timeout:
        print("❌ 請求超時")
    
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
    
    print("\n" + "=" * 50)
    print("✅ 測試完成")

if __name__ == "__main__":
    test_interaction_api()

























