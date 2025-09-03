#!/usr/bin/env python3
"""
系統性探索 FinLab 資料庫實際可用的資料表
找出正確的資料表名稱
"""

import os
import pandas as pd
import finlab
from finlab import data
from dotenv import load_dotenv
import time

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

def test_common_data_tables():
    """測試常見的資料表名稱"""
    print("\n📋 測試常見資料表名稱...")
    
    # 根據之前測試結果，我們知道這些是可用的
    known_working_tables = [
        'financial_statement:營業利益',
        'financial_statement:稅前淨利',
        'financial_statement:營業成本',
        'financial_statement:營業費用',
        'financial_statement:流動資產',
        'financial_statement:流動負債',
        'financial_statement:現金及約當現金',
        'financial_statement:存貨',
        'price:收盤價',
        'price:開盤價',
        'price:最高價',
        'price:最低價',
        'price:成交股數'
    ]
    
    # 測試這些已知可用的表格
    for table_name in known_working_tables:
        try:
            df = data.get(table_name)
            print(f"✅ {table_name}: 可用")
            if '2330' in df.columns:
                recent_data = df['2330'].dropna().tail(1)
                if not recent_data.empty:
                    value = recent_data.iloc[0]
                    formatted_value = format_large_number(value)
                    print(f"   📊 2330 最新資料: {formatted_value}")
        except Exception as e:
            print(f"❌ {table_name}: 不可用 - {e}")

def explore_financial_statement_tables():
    """探索 financial_statement 相關的表格"""
    print("\n📈 探索 financial_statement 表格...")
    
    # 可能的財務報表項目
    financial_items = [
        '營業收入',
        '營業成本',
        '營業費用',
        '營業利益',
        '稅前淨利',
        '稅後淨利',
        '淨利',
        '總資產',
        '股東權益',
        '流動資產',
        '流動負債',
        '長期負債',
        '現金及約當現金',
        '應收帳款',
        '存貨',
        '固定資產',
        '無形資產',
        '商譽',
        '投資',
        '短期投資',
        '長期投資',
        '研發費用',
        '資本支出',
        '折舊',
        '攤銷',
        '利息費用',
        '利息收入',
        '股利收入',
        '投資收益',
        '匯兌損益',
        '其他收入',
        '其他費用',
        '所得稅費用',
        '少數股權損益',
        '基本每股盈餘',
        '稀釋每股盈餘',
        '每股淨值',
        '每股現金股利',
        '每股股票股利',
        '股利發放率',
        '本益比',
        '股價淨值比',
        '股東權益報酬率',
        '資產報酬率',
        '營業利益率',
        '淨利率',
        '毛利率',
        '負債比率',
        '流動比率',
        '速動比率',
        '現金比率',
        '利息保障倍數',
        '存貨週轉率',
        '應收帳款週轉率',
        '固定資產週轉率',
        '總資產週轉率',
        '股東權益週轉率',
        '現金週轉率',
        '營運資金週轉率'
    ]
    
    available_tables = []
    
    for item in financial_items:
        table_name = f'financial_statement:{item}'
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
            print(f"❌ {table_name}: 不可用")
    
    return available_tables

def explore_revenue_tables():
    """探索營收相關的表格"""
    print("\n📊 探索營收相關表格...")
    
    revenue_items = [
        '營收',
        '月營收',
        '年營收',
        '累計營收',
        '營收成長率',
        '月營收成長率',
        '年營收成長率',
        '營收季增率',
        '營收年增率',
        '營收月增率',
        '營收累計成長率'
    ]
    
    available_tables = []
    
    for item in revenue_items:
        # 嘗試不同的前綴
        prefixes = ['revenue:', 'monthly_revenue:', 'annual_revenue:', '']
        
        for prefix in prefixes:
            table_name = f'{prefix}{item}'
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
                break
                        
            except Exception as e:
                continue
    
    return available_tables

def explore_eps_tables():
    """探索每股盈餘相關的表格"""
    print("\n💰 探索每股盈餘相關表格...")
    
    eps_items = [
        '每股盈餘',
        '基本每股盈餘',
        '稀釋每股盈餘',
        '每股盈餘成長率',
        '每股盈餘季增率',
        '每股盈餘年增率'
    ]
    
    available_tables = []
    
    for item in eps_items:
        # 嘗試不同的前綴
        prefixes = ['eps:', 'earnings_per_share:', '']
        
        for prefix in prefixes:
            table_name = f'{prefix}{item}'
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
                break
                        
            except Exception as e:
                continue
    
    return available_tables

if __name__ == "__main__":
    print("🚀 開始系統性探索 FinLab 資料庫...")
    
    # 測試登入
    if not test_finlab_login():
        exit(1)
    
    # 測試已知可用的表格
    test_common_data_tables()
    
    # 探索各種表格
    financial_tables = explore_financial_statement_tables()
    revenue_tables = explore_revenue_tables()
    eps_tables = explore_eps_tables()
    
    print(f"\n📋 探索結果總結:")
    print(f"   財務報表表格: {len(financial_tables)} 個可用")
    print(f"   營收相關表格: {len(revenue_tables)} 個可用")
    print(f"   每股盈餘表格: {len(eps_tables)} 個可用")
    
    print("\n✅ 探索完成")


