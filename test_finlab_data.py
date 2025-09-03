#!/usr/bin/env python3
"""
測試 FinLab 營收和財報資料取得
驗證 API Key 設定和數字格式化
"""

import os
import pandas as pd
import finlab
from finlab import data
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

def format_large_number(num):
    """格式化大數字，例如 1204532131 -> 12億453萬"""
    if pd.isna(num) or num == 0:
        return "0"
    
    num = int(num)
    
    if num >= 100000000:  # 億
        yi = num // 100000000
        wan = (num % 100000000) // 10000
        if wan > 0:
            return f"{yi}億{wan}萬"
        else:
            return f"{yi}億"
    elif num >= 10000:  # 萬
        wan = num // 10000
        return f"{wan}萬"
    else:
        return str(num)

def test_finlab_login():
    """測試 FinLab 登入"""
    print("🔐 測試 FinLab 登入...")
    
    api_key = os.getenv("FINLAB_API_KEY")
    if not api_key:
        print("❌ FINLAB_API_KEY 未設定")
        return False
    
    try:
        finlab.login(api_key)
        print("✅ FinLab 登入成功")
        return True
    except Exception as e:
        print(f"❌ FinLab 登入失敗: {e}")
        return False

def test_revenue_data():
    """測試營收資料取得"""
    print("\n📊 測試營收資料取得 (2330)...")
    
    try:
        # 取得營收資料
        revenue_df = data.get('revenue:營收')
        
        if '2330' not in revenue_df.columns:
            print("❌ 2330 不在營收資料中")
            return
        
        # 取得最近幾筆資料
        recent_revenue = revenue_df['2330'].dropna().tail(5)
        
        print(f"✅ 成功取得 2330 營收資料")
        print(f"   最近 5 筆資料:")
        
        for date, value in recent_revenue.items():
            formatted_value = format_large_number(value)
            print(f"   {date.strftime('%Y-%m')}: {formatted_value}")
            
    except Exception as e:
        print(f"❌ 營收資料取得失敗: {e}")

def test_financial_data():
    """測試財報資料取得"""
    print("\n📈 測試財報資料取得 (2330)...")
    
    try:
        # 取得資產負債表資料
        balance_sheet = data.get('financial_statement:資產負債表')
        
        if '2330' not in balance_sheet.columns:
            print("❌ 2330 不在財報資料中")
            return
        
        # 取得最近幾筆資料
        recent_financial = balance_sheet['2330'].dropna().tail(3)
        
        print(f"✅ 成功取得 2330 財報資料")
        print(f"   最近 3 筆資料:")
        
        for date, value in recent_financial.items():
            formatted_value = format_large_number(value)
            print(f"   {date.strftime('%Y-%m')}: {formatted_value}")
            
    except Exception as e:
        print(f"❌ 財報資料取得失敗: {e}")

def test_profit_data():
    """測試獲利資料取得"""
    print("\n💰 測試獲利資料取得 (2330)...")
    
    try:
        # 取得稅後淨利資料
        net_profit = data.get('financial_statement:稅後淨利')
        
        if '2330' not in net_profit.columns:
            print("❌ 2330 不在獲利資料中")
            return
        
        # 取得最近幾筆資料
        recent_profit = net_profit['2330'].dropna().tail(3)
        
        print(f"✅ 成功取得 2330 獲利資料")
        print(f"   最近 3 筆資料:")
        
        for date, value in recent_profit.items():
            formatted_value = format_large_number(value)
            print(f"   {date.strftime('%Y-%m')}: {formatted_value}")
            
    except Exception as e:
        print(f"❌ 獲利資料取得失敗: {e}")

if __name__ == "__main__":
    print("🚀 開始測試 FinLab 資料取得...")
    
    # 測試登入
    if not test_finlab_login():
        exit(1)
    
    # 測試各種資料
    test_revenue_data()
    test_financial_data()
    test_profit_data()
    
    print("\n✅ 測試完成")


