#!/usr/bin/env python3
"""
測試正確的 FinLab 資料表調用方式
基於 FinLab 資料庫的實際結構
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
    
    # 月營收相關指標
    revenue_metrics = [
        'monthly_revenue:當月營收',
        'monthly_revenue:上月營收',
        'monthly_revenue:去年當月營收',
        'monthly_revenue:上月比較增減(%)',
        'monthly_revenue:去年同月增減(%)',
        'monthly_revenue:當月累計營收',
        'monthly_revenue:去年累計營收',
        'monthly_revenue:前期比較增減(%)'
    ]
    
    for metric in revenue_metrics:
        try:
            df = data.get(metric)
            if '2330' in df.columns:
                recent_data = df['2330'].dropna().tail(1)
                if not recent_data.empty:
                    value = recent_data.iloc[0]
                    if '營收' in metric:
                        formatted_value = format_large_number(value)
                        print(f"✅ {metric}: {formatted_value}")
                    else:
                        print(f"✅ {metric}: {value:.2f}%")
                else:
                    print(f"⚠️  {metric}: 無最新資料")
            else:
                print(f"❌ {metric}: 2330 不在資料中")
        except Exception as e:
            print(f"❌ {metric}: 錯誤 - {e}")

def test_fundamental_features():
    """測試財務指標資料"""
    print("\n📈 測試財務指標資料 (2330)...")
    
    # 財務指標相關指標
    fundamental_metrics = [
        'fundamental_features:營業利益',
        'fundamental_features:EBITDA',
        'fundamental_features:營運現金流',
        'fundamental_features:歸屬母公司淨利',
        'fundamental_features:營業毛利率',
        'fundamental_features:營業利益率',
        'fundamental_features:稅前淨利率',
        'fundamental_features:稅後淨利率',
        'fundamental_features:流動資產',
        'fundamental_features:流動負債',
        'fundamental_features:ROA稅後息前',
        'fundamental_features:ROE稅後'
    ]
    
    for metric in fundamental_metrics:
        try:
            df = data.get(metric)
            if '2330' in df.columns:
                recent_data = df['2330'].dropna().tail(1)
                if not recent_data.empty:
                    value = recent_data.iloc[0]
                    if '率' in metric or 'ROA' in metric or 'ROE' in metric:
                        print(f"✅ {metric}: {value:.2f}%")
                    else:
                        formatted_value = format_large_number(value)
                        print(f"✅ {metric}: {formatted_value}")
                else:
                    print(f"⚠️  {metric}: 無最新資料")
            else:
                print(f"❌ {metric}: 2330 不在資料中")
        except Exception as e:
            print(f"❌ {metric}: 錯誤 - {e}")

def test_multiple_stocks():
    """測試多檔股票的資料"""
    print("\n📋 測試多檔股票資料...")
    
    test_stocks = ['2330', '2317', '2454', '1301', '2881']
    
    # 測試月營收
    try:
        revenue_df = data.get('monthly_revenue:當月營收')
        print(f"✅ 月營收資料可用，包含 {len(revenue_df.columns)} 檔股票")
        
        for stock in test_stocks:
            if stock in revenue_df.columns:
                recent_data = revenue_df[stock].dropna().tail(1)
                if not recent_data.empty:
                    revenue = recent_data.iloc[0]
                    formatted_revenue = format_large_number(revenue)
                    print(f"   {stock}: 營收 {formatted_revenue}")
    except Exception as e:
        print(f"❌ 月營收資料測試失敗: {e}")
    
    # 測試財務指標
    try:
        profit_df = data.get('fundamental_features:營業利益')
        print(f"✅ 營業利益資料可用，包含 {len(profit_df.columns)} 檔股票")
        
        for stock in test_stocks:
            if stock in profit_df.columns:
                recent_data = profit_df[stock].dropna().tail(1)
                if not recent_data.empty:
                    profit = recent_data.iloc[0]
                    formatted_profit = format_large_number(profit)
                    print(f"   {stock}: 營業利益 {formatted_profit}")
    except Exception as e:
        print(f"❌ 營業利益資料測試失敗: {e}")

def test_growth_rates():
    """測試成長率資料"""
    print("\n📈 測試成長率資料 (2330)...")
    
    # 成長率相關指標
    growth_metrics = [
        'monthly_revenue:上月比較增減(%)',
        'monthly_revenue:去年同月增減(%)',
        'monthly_revenue:前期比較增減(%)'
    ]
    
    for metric in growth_metrics:
        try:
            df = data.get(metric)
            if '2330' in df.columns:
                recent_data = df['2330'].dropna().tail(3)
                print(f"✅ {metric}:")
                for date, value in recent_data.items():
                    print(f"   {date}: {value:.2f}%")
        except Exception as e:
            print(f"❌ {metric}: 錯誤 - {e}")

if __name__ == "__main__":
    print("🚀 測試正確的 FinLab 資料表調用方式...")
    
    # 測試登入
    if not test_finlab_login():
        exit(1)
    
    # 測試各種資料
    test_monthly_revenue()
    test_fundamental_features()
    test_multiple_stocks()
    test_growth_rates()
    
    print("\n✅ 測試完成")


