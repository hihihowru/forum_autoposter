#!/usr/bin/env python3
"""
測試實際可用的 FinLab 資料表
基於 search 結果建立正確的 API
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

def test_monthly_revenue():
    """測試月營收資料"""
    print("\n📊 測試月營收資料 (2330)...")
    
    try:
        # 取得月營收資料
        revenue_df = data.get('monthly_revenue')
        
        if '2330' in revenue_df.columns:
            recent_data = revenue_df['2330'].dropna().tail(1)
            if not recent_data.empty:
                latest_data = recent_data.iloc[0]
                print(f"✅ 2330 月營收資料:")
                print(f"   當月營收: {format_large_number(latest_data.get('當月營收', 0))}")
                print(f"   上月營收: {format_large_number(latest_data.get('上月營收', 0))}")
                print(f"   去年當月營收: {format_large_number(latest_data.get('去年當月營收', 0))}")
                print(f"   上月比較增減: {latest_data.get('上月比較增減(%)', 0):.2f}%")
                print(f"   去年同月增減: {latest_data.get('去年同月增減(%)', 0):.2f}%")
                print(f"   當月累計營收: {format_large_number(latest_data.get('當月累計營收', 0))}")
                print(f"   前期比較增減: {latest_data.get('前期比較增減(%)', 0):.2f}%")
        else:
            print("❌ 2330 不在月營收資料中")
            
    except Exception as e:
        print(f"❌ 月營收資料取得失敗: {e}")

def test_fundamental_features():
    """測試財務指標資料"""
    print("\n📈 測試財務指標資料 (2330)...")
    
    try:
        # 取得財務指標資料
        features_df = data.get('fundamental_features')
        
        if '2330' in features_df.columns:
            recent_data = features_df['2330'].dropna().tail(1)
            if not recent_data.empty:
                latest_data = recent_data.iloc[0]
                print(f"✅ 2330 財務指標:")
                print(f"   營收成長率: {latest_data.get('營收成長率', 0):.2f}%")
                print(f"   營業毛利成長率: {latest_data.get('營業毛利成長率', 0):.2f}%")
                print(f"   營業利益成長率: {latest_data.get('營業利益成長率', 0):.2f}%")
                print(f"   稅前淨利成長率: {latest_data.get('稅前淨利成長率', 0):.2f}%")
                print(f"   稅後淨利成長率: {latest_data.get('稅後淨利成長率', 0):.2f}%")
                print(f"   經常利益成長率: {latest_data.get('經常利益成長率', 0):.2f}%")
                print(f"   資產總額成長率: {latest_data.get('資產總額成長率', 0):.2f}%")
                print(f"   淨值成長率: {latest_data.get('淨值成長率', 0):.2f}%")
        else:
            print("❌ 2330 不在財務指標資料中")
            
    except Exception as e:
        print(f"❌ 財務指標資料取得失敗: {e}")

def test_eps_data():
    """測試每股盈餘資料"""
    print("\n💰 測試每股盈餘資料 (2330)...")
    
    try:
        # 取得每股盈餘資料
        eps_df = data.get('financial_statement:每股盈餘')
        
        if '2330' in eps_df.columns:
            recent_data = eps_df['2330'].dropna().tail(3)
            print(f"✅ 2330 每股盈餘資料:")
            for date, value in recent_data.items():
                print(f"   {date.strftime('%Y-%m')}: {value:.2f}")
        else:
            print("❌ 2330 不在每股盈餘資料中")
            
    except Exception as e:
        print(f"❌ 每股盈餘資料取得失敗: {e}")

def test_multiple_stocks():
    """測試多檔股票的資料"""
    print("\n📋 測試多檔股票資料...")
    
    test_stocks = ['2330', '2317', '2454', '1301', '2881']
    
    # 測試月營收
    try:
        revenue_df = data.get('monthly_revenue')
        print(f"✅ 月營收資料可用，包含 {len(revenue_df.columns)} 檔股票")
        
        for stock in test_stocks:
            if stock in revenue_df.columns:
                recent_data = revenue_df[stock].dropna().tail(1)
                if not recent_data.empty:
                    latest_data = recent_data.iloc[0]
                    revenue = latest_data.get('當月營收', 0)
                    growth = latest_data.get('去年同月增減(%)', 0)
                    print(f"   {stock}: 營收 {format_large_number(revenue)}, 年增 {growth:.2f}%")
    except Exception as e:
        print(f"❌ 月營收資料測試失敗: {e}")
    
    # 測試財務指標
    try:
        features_df = data.get('fundamental_features')
        print(f"✅ 財務指標資料可用，包含 {len(features_df.columns)} 檔股票")
        
        for stock in test_stocks:
            if stock in features_df.columns:
                recent_data = features_df[stock].dropna().tail(1)
                if not recent_data.empty:
                    latest_data = recent_data.iloc[0]
                    revenue_growth = latest_data.get('營收成長率', 0)
                    profit_growth = latest_data.get('營業利益成長率', 0)
                    print(f"   {stock}: 營收成長 {revenue_growth:.2f}%, 營業利益成長 {profit_growth:.2f}%")
    except Exception as e:
        print(f"❌ 財務指標資料測試失敗: {e}")

if __name__ == "__main__":
    print("🚀 測試實際可用的 FinLab 資料表...")
    
    # 測試登入
    if not test_finlab_login():
        exit(1)
    
    # 測試各種資料
    test_monthly_revenue()
    test_fundamental_features()
    test_eps_data()
    test_multiple_stocks()
    
    print("\n✅ 測試完成")


