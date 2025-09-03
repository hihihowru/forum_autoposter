#!/usr/bin/env python3
"""
探索 FinLab 資料庫可用的表格
使用 data.get 方式取得資料
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

def explore_financial_data():
    """探索財務資料相關的表格"""
    print("\n📈 探索財務資料表格...")
    
    # 根據 FinLab 資料庫可能的表格名稱
    financial_tables = [
        'financial_statement:營業利益',
        'financial_statement:營業收入',
        'financial_statement:稅後淨利',
        'financial_statement:稅前淨利',
        'financial_statement:營業成本',
        'financial_statement:營業費用',
        'financial_statement:總資產',
        'financial_statement:股東權益',
        'financial_statement:流動資產',
        'financial_statement:流動負債',
        'financial_statement:長期負債',
        'financial_statement:現金及約當現金',
        'financial_statement:應收帳款',
        'financial_statement:存貨',
        'financial_statement:固定資產',
        'financial_statement:無形資產',
        'financial_statement:商譽',
        'financial_statement:投資',
        'financial_statement:短期投資',
        'financial_statement:長期投資'
    ]
    
    available_tables = []
    
    for table_name in financial_tables:
        try:
            df = data.get(table_name)
            print(f"✅ {table_name}: 可用")
            available_tables.append(table_name)
            
            if '2330' in df.columns:
                recent_data = df['2330'].dropna().tail(1)
                if not recent_data.empty:
                    value = recent_data.iloc[0]
                    formatted_value = format_large_number(value)
                    print(f"   📊 2330 最新資料: {formatted_value}")
                    
        except Exception as e:
            print(f"❌ {table_name}: 不可用 - {e}")
    
    return available_tables

def explore_revenue_data():
    """探索營收相關的表格"""
    print("\n📊 探索營收資料表格...")
    
    revenue_tables = [
        'revenue:營收',
        'revenue:月營收',
        'revenue:年營收',
        'revenue:累計營收',
        'revenue:營收成長率',
        'revenue:月營收成長率',
        'revenue:年營收成長率',
        'monthly_revenue',
        'annual_revenue',
        '營收',
        '月營收',
        '年營收'
    ]
    
    available_tables = []
    
    for table_name in revenue_tables:
        try:
            df = data.get(table_name)
            print(f"✅ {table_name}: 可用")
            available_tables.append(table_name)
            
            if '2330' in df.columns:
                recent_data = df['2330'].dropna().tail(1)
                if not recent_data.empty:
                    value = recent_data.iloc[0]
                    formatted_value = format_large_number(value)
                    print(f"   📊 2330 最新資料: {formatted_value}")
                    
        except Exception as e:
            print(f"❌ {table_name}: 不可用 - {e}")
    
    return available_tables

def explore_other_data():
    """探索其他可能的資料表格"""
    print("\n🔍 探索其他資料表格...")
    
    other_tables = [
        'eps:每股盈餘',
        'eps:基本每股盈餘',
        'eps:稀釋每股盈餘',
        'dividend:股利',
        'dividend:現金股利',
        'dividend:股票股利',
        'pe:本益比',
        'pb:股價淨值比',
        'roe:股東權益報酬率',
        'roa:資產報酬率',
        'debt_ratio:負債比率',
        'current_ratio:流動比率',
        'quick_ratio:速動比率',
        'inventory_turnover:存貨週轉率',
        'receivables_turnover:應收帳款週轉率'
    ]
    
    available_tables = []
    
    for table_name in other_tables:
        try:
            df = data.get(table_name)
            print(f"✅ {table_name}: 可用")
            available_tables.append(table_name)
            
            if '2330' in df.columns:
                recent_data = df['2330'].dropna().tail(1)
                if not recent_data.empty:
                    value = recent_data.iloc[0]
                    formatted_value = format_large_number(value)
                    print(f"   📊 2330 最新資料: {formatted_value}")
                    
        except Exception as e:
            print(f"❌ {table_name}: 不可用 - {e}")
    
    return available_tables

def test_data_structure(table_name):
    """測試特定表格的資料結構"""
    print(f"\n🔬 測試表格結構: {table_name}")
    
    try:
        df = data.get(table_name)
        print(f"✅ 表格載入成功")
        print(f"   資料形狀: {df.shape}")
        print(f"   欄位數量: {len(df.columns)}")
        print(f"   日期範圍: {df.index.min()} 到 {df.index.max()}")
        
        if '2330' in df.columns:
            print(f"   ✅ 2330 資料存在")
            recent_data = df['2330'].dropna().tail(3)
            print(f"   最近 3 筆資料:")
            for date, value in recent_data.items():
                formatted_value = format_large_number(value)
                print(f"     {date.strftime('%Y-%m')}: {formatted_value}")
        else:
            print(f"   ❌ 2330 資料不存在")
            sample_stocks = df.columns[:5].tolist()
            print(f"   範例股票: {sample_stocks}")
            
    except Exception as e:
        print(f"❌ 表格結構測試失敗: {e}")

if __name__ == "__main__":
    print("🚀 開始探索 FinLab 資料庫...")
    
    # 測試登入
    if not test_finlab_login():
        exit(1)
    
    # 探索各種資料表格
    financial_tables = explore_financial_data()
    revenue_tables = explore_revenue_data()
    other_tables = explore_other_data()
    
    # 測試已知可用的表格結構
    if financial_tables:
        test_data_structure(financial_tables[0])
    
    print(f"\n📋 總結:")
    print(f"   財務資料表格: {len(financial_tables)} 個可用")
    print(f"   營收資料表格: {len(revenue_tables)} 個可用")
    print(f"   其他資料表格: {len(other_tables)} 個可用")
    
    print("\n✅ 探索完成")


