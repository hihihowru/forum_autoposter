#!/usr/bin/env python3
"""
測試 CMoney API 獲取文章互動數據
"""

import requests
import json
import os
from datetime import datetime

def test_cmoney_article_api():
    """測試 CMoney Article API"""
    
    # API 配置
    article_id = "173337593"
    api_url = f"https://api.cmoney.tw/api/Article/{article_id}"
    
    # 請求標頭
    headers = {
        "X-Version": "2.0",
        "cmoneyapi-trace-context": "dashboard-test",
        "Content-Type": "application/json",
        "User-Agent": "Dashboard-Test/1.0"
    }
    
    print("🚀 測試 CMoney Article API")
    print("=" * 60)
    print(f"📝 Article ID: {article_id}")
    print(f"🔗 API URL: {api_url}")
    print(f"📋 Headers: {json.dumps(headers, indent=2)}")
    print("=" * 60)
    
    try:
        # 發送 GET 請求
        print("📤 發送請求...")
        response = requests.get(api_url, headers=headers, timeout=30)
        
        print(f"📊 響應狀態碼: {response.status_code}")
        print(f"📋 響應標頭: {dict(response.headers)}")
        
        if response.status_code == 200:
            # 成功響應
            data = response.json()
            print("✅ API 調用成功！")
            print("=" * 60)
            
            # 格式化輸出響應數據
            print("📄 響應數據:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # 提取互動數據
            if 'commentCount' in data:
                print("\n📊 互動數據摘要:")
                print("-" * 40)
                print(f"留言數 (commentCount): {data.get('commentCount', 0)}")
                print(f"捐贈數 (donation): {data.get('donation', 0)}")
                print(f"收藏數 (collectedCount): {data.get('collectedCount', 0)}")
                
                # 表情數據
                emoji_count = data.get('emojiCount', {})
                if emoji_count:
                    print("\n😀 表情數據:")
                    for emoji, count in emoji_count.items():
                        print(f"  {emoji}: {count}")
                
                # 計算總互動數
                total_interactions = data.get('commentCount', 0) + data.get('collectedCount', 0)
                if emoji_count:
                    total_interactions += sum(emoji_count.values())
                
                print(f"\n📈 總互動數: {total_interactions}")
                
                return {
                    "success": True,
                    "data": data,
                    "interactions": {
                        "comments": data.get('commentCount', 0),
                        "collections": data.get('collectedCount', 0),
                        "donations": data.get('donation', 0),
                        "emojis": emoji_count,
                        "total": total_interactions
                    }
                }
            else:
                print("⚠️ 響應中沒有找到互動數據欄位")
                return {"success": True, "data": data, "interactions": None}
                
        else:
            # 錯誤響應
            print(f"❌ API 調用失敗，狀態碼: {response.status_code}")
            print(f"📄 錯誤響應: {response.text}")
            return {"success": False, "error": response.text, "status_code": response.status_code}
            
    except requests.exceptions.Timeout:
        print("⏰ 請求超時")
        return {"success": False, "error": "Request timeout"}
    except requests.exceptions.ConnectionError:
        print("🔌 連接錯誤")
        return {"success": False, "error": "Connection error"}
    except requests.exceptions.RequestException as e:
        print(f"❌ 請求錯誤: {e}")
        return {"success": False, "error": str(e)}
    except json.JSONDecodeError as e:
        print(f"❌ JSON 解析錯誤: {e}")
        print(f"📄 原始響應: {response.text}")
        return {"success": False, "error": "JSON decode error", "raw_response": response.text}
    except Exception as e:
        print(f"❌ 未知錯誤: {e}")
        return {"success": False, "error": str(e)}

def test_multiple_articles():
    """測試多個文章 ID"""
    print("\n🔄 測試多個文章 ID...")
    print("=" * 60)
    
    # 測試多個文章 ID
    test_article_ids = [
        "173337593",  # 您提供的 ID
        "173337594",  # 相近的 ID
        "173337595",  # 相近的 ID
    ]
    
    results = []
    
    for article_id in test_article_ids:
        print(f"\n📝 測試 Article ID: {article_id}")
        print("-" * 40)
        
        result = test_cmoney_article_api()
        results.append({
            "article_id": article_id,
            "result": result
        })
        
        if result["success"]:
            interactions = result.get("interactions")
            if interactions:
                print(f"✅ 成功獲取互動數據: {interactions['total']} 總互動")
            else:
                print("⚠️ 成功但無互動數據")
        else:
            print(f"❌ 失敗: {result.get('error', 'Unknown error')}")
    
    return results

def analyze_api_response_structure():
    """分析 API 響應結構"""
    print("\n🔍 分析 API 響應結構...")
    print("=" * 60)
    
    result = test_cmoney_article_api()
    
    if result["success"] and result["data"]:
        data = result["data"]
        
        print("📋 響應數據結構分析:")
        print("-" * 40)
        
        # 分析主要欄位
        main_fields = [
            "commentCount", "donation", "collectedCount", "emojiCount",
            "id", "title", "content", "author", "publishTime", "updateTime"
        ]
        
        for field in main_fields:
            if field in data:
                value = data[field]
                if isinstance(value, dict):
                    print(f"✅ {field}: {type(value).__name__} (包含 {len(value)} 個子欄位)")
                    if field == "emojiCount":
                        for emoji, count in value.items():
                            print(f"   - {emoji}: {count}")
                else:
                    print(f"✅ {field}: {value}")
            else:
                print(f"❌ {field}: 不存在")
        
        # 分析其他欄位
        other_fields = [key for key in data.keys() if key not in main_fields]
        if other_fields:
            print(f"\n📝 其他欄位 ({len(other_fields)} 個):")
            for field in other_fields[:10]:  # 只顯示前10個
                value = data[field]
                print(f"  - {field}: {type(value).__name__}")
    
    return result

def main():
    """主函數"""
    print("🧪 CMoney API 測試工具")
    print("=" * 60)
    print(f"⏰ 測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 測試單個文章
    print("\n1️⃣ 測試單個文章 API")
    result = test_cmoney_article_api()
    
    # 2. 分析響應結構
    print("\n2️⃣ 分析 API 響應結構")
    analyze_api_response_structure()
    
    # 3. 測試多個文章
    print("\n3️⃣ 測試多個文章 ID")
    multiple_results = test_multiple_articles()
    
    # 4. 總結
    print("\n📊 測試總結")
    print("=" * 60)
    
    successful_tests = sum(1 for r in multiple_results if r["result"]["success"])
    total_tests = len(multiple_results)
    
    print(f"✅ 成功測試: {successful_tests}/{total_tests}")
    
    if successful_tests > 0:
        print("\n🎯 可用於儀表板的數據:")
        print("- commentCount: 留言數")
        print("- collectedCount: 收藏數") 
        print("- donation: 捐贈數")
        print("- emojiCount: 表情數據 (like, dislike, laugh, money, shock, cry, think, angry)")
        print("- 總互動數: commentCount + collectedCount + 所有表情數")
    
    print("\n✅ 測試完成！")

if __name__ == "__main__":
    main()
