#!/usr/bin/env python3
"""
測試 FinLab 營收和財報資料取得
驗證正確的資料名稱
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

def test_available_data():
    """測試可用的資料名稱"""
    print("\n📋 測試可用的資料名稱...")
    
    # 常見的資料名稱
    data_names = [
        'revenue:營收',
        'revenue:月營收',
        'revenue:年營收',
        'financial_statement:資產負債表',
        'financial_statement:損益表',
        'financial_statement:稅後淨利',
        'financial_statement:營業收入',
        'financial_statement:營業利益',
        'price:收盤價',
        'price:開盤價',
        'price:最高價',
        'price:最低價',
        'price:成交股數'
    ]
    
    for name in data_names:
        try:
            df = data.get(name)
            print(f"✅ {name}: 可用")
            if '2330' in df.columns:
                recent_data = df['2330'].dropna().tail(1)
                if not recent_data.empty:
                    value = recent_data.iloc[0]
                    formatted_value = format_large_number(value)
                    print(f"   📊 2330 最新資料: {formatted_value}")
        except Exception as e:
            print(f"❌ {name}: 不可用 - {e}")

def test_revenue_alternatives():
    """測試營收相關的替代名稱"""
    print("\n📊 測試營收相關資料...")
    
    revenue_names = [
        'revenue',
        'monthly_revenue',
        'annual_revenue',
        '營收',
        '月營收',
        '年營收'
    ]
    
    for name in revenue_names:
        try:
            df = data.get(name)
            print(f"✅ {name}: 可用")
            if '2330' in df.columns:
                recent_data = df['2330'].dropna().tail(1)
                if not recent_data.empty:
                    value = recent_data.iloc[0]
                    formatted_value = format_large_number(value)
                    print(f"   📊 2330 最新資料: {formatted_value}")
        except Exception as e:
            print(f"❌ {name}: 不可用")

def test_financial_alternatives():
    """測試財報相關的替代名稱"""
    print("\n📈 測試財報相關資料...")
    
    financial_names = [
        'financial_statement',
        'balance_sheet',
        'income_statement',
        'net_profit',
        '稅後淨利',
        '營業收入',
        '營業利益'
    ]
    
    for name in financial_names:
        try:
            df = data.get(name)
            print(f"✅ {name}: 可用")
            if '2330' in df.columns:
                recent_data = df['2330'].dropna().tail(1)
                if not recent_data.empty:
                    value = recent_data.iloc[0]
                    formatted_value = format_large_number(value)
                    print(f"   📊 2330 最新資料: {formatted_value}")
        except Exception as e:
            print(f"❌ {name}: 不可用")

if __name__ == "__main__":
    print("🚀 開始測試 FinLab 資料名稱...")
    
    # 測試登入
    if not test_finlab_login():
        exit(1)
    
    # 測試各種資料名稱
    test_available_data()
    test_revenue_alternatives()
    test_financial_alternatives()
    
    print("\n✅ 測試完成")


