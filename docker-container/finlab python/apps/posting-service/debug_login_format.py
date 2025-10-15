#!/usr/bin/env python3
"""
詳細檢查 KOL 登入請求格式
"""

import requests
import json

def test_login_request_format():
    """測試登入請求格式"""
    
    print("🔍 詳細檢查 KOL 登入請求格式")
    print("=" * 50)
    
    # 測試不同的登入格式
    login_url = "https://social.cmoney.tw/identity/token"
    
    # 格式 1: 原本的格式
    print("📋 測試格式 1: 原本的格式")
    data1 = {
        "grant_type": "password",
        "login_method": "email",
        "client_id": "cmstockcommunity",
        "account": "forum_150@cmoney.com.tw",
        "password": "N9t1kY3x"
    }
    
    headers1 = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    try:
        response1 = requests.post(login_url, data=data1, headers=headers1)
        print(f"📊 格式 1 回應: {response1.status_code}")
        print(f"📝 格式 1 內容: {response1.text}")
    except Exception as e:
        print(f"❌ 格式 1 異常: {e}")
    
    print("\n" + "-" * 30)
    
    # 格式 2: 簡化格式
    print("📋 測試格式 2: 簡化格式")
    data2 = {
        "email": "forum_150@cmoney.com.tw",
        "password": "N9t1kY3x"
    }
    
    headers2 = {
        "Content-Type": "application/json"
    }
    
    try:
        response2 = requests.post(login_url, json=data2, headers=headers2)
        print(f"📊 格式 2 回應: {response2.status_code}")
        print(f"📝 格式 2 內容: {response2.text}")
    except Exception as e:
        print(f"❌ 格式 2 異常: {e}")
    
    print("\n" + "-" * 30)
    
    # 格式 3: 不同的 client_id
    print("📋 測試格式 3: 不同的 client_id")
    data3 = {
        "grant_type": "password",
        "login_method": "email",
        "client_id": "app",  # 嘗試不同的 client_id
        "account": "forum_150@cmoney.com.tw",
        "password": "N9t1kY3x"
    }
    
    headers3 = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    try:
        response3 = requests.post(login_url, data=data3, headers=headers3)
        print(f"📊 格式 3 回應: {response3.status_code}")
        print(f"📝 格式 3 內容: {response3.text}")
    except Exception as e:
        print(f"❌ 格式 3 異常: {e}")

def test_different_accounts():
    """測試不同的帳號格式"""
    
    print("\n" + "=" * 50)
    print("🔍 測試不同的帳號格式")
    print("=" * 50)
    
    login_url = "https://social.cmoney.tw/identity/token"
    
    # 測試不同的帳號格式
    test_accounts = [
        "forum_150@cmoney.com.tw",
        "150@cmoney.com.tw",
        "forum150@cmoney.com.tw",
        "kol150@cmoney.com.tw"
    ]
    
    for account in test_accounts:
        print(f"\n🔐 測試帳號: {account}")
        
        data = {
            "grant_type": "password",
            "login_method": "email",
            "client_id": "cmstockcommunity",
            "account": account,
            "password": "N9t1kY3x"
        }
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        try:
            response = requests.post(login_url, data=data, headers=headers)
            print(f"📊 回應: {response.status_code}")
            
            if response.status_code == 200:
                print(f"✅ 成功! 正確的帳號格式: {account}")
                return account
            else:
                print(f"❌ 失敗: {response.text}")
                
        except Exception as e:
            print(f"❌ 異常: {e}")
    
    return None

if __name__ == "__main__":
    print("🚀 詳細檢查 KOL 登入請求格式")
    
    # 測試不同的請求格式
    test_login_request_format()
    
    # 測試不同的帳號格式
    correct_account = test_different_accounts()
    
    print("\n" + "=" * 50)
    print("🎯 檢查結果")
    print("=" * 50)
    
    if correct_account:
        print(f"🎉 找到正確的帳號格式: {correct_account}")
    else:
        print("❌ 所有帳號格式都失敗")
        print("💡 建議:")
        print("   1. 檢查 KOL 帳號是否還有效")
        print("   2. 確認密碼是否正確")
        print("   3. 檢查帳號格式是否正確")
        print("   4. 可能需要重新創建 KOL 帳號")


