#!/usr/bin/env python3
"""
探索 FinLab 資料庫實際可用的資料表
使用正確的方法查看 schema
"""

import os
import pandas as pd
import finlab
from finlab import data
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

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

def explore_finlab_database():
    """探索 FinLab 資料庫的實際結構"""
    print("\n🔍 探索 FinLab 資料庫結構...")
    
    # 嘗試查看 FinLab 資料庫的可用資料表
    try:
        # 檢查是否有列出資料表的方法
        print("檢查 FinLab 資料庫方法...")
        print(f"FinLab 模組屬性: {dir(finlab)}")
        print(f"Data 模組屬性: {dir(data)}")
        
        # 嘗試獲取資料庫資訊
        if hasattr(data, 'list_datasets'):
            print("找到 list_datasets 方法")
            datasets = data.list_datasets()
            print(f"可用資料集: {datasets}")
        elif hasattr(data, 'get_datasets'):
            print("找到 get_datasets 方法")
            datasets = data.get_datasets()
            print(f"可用資料集: {datasets}")
        else:
            print("未找到列出資料集的方法")
            
    except Exception as e:
        print(f"探索資料庫結構時發生錯誤: {e}")

def test_known_working_tables():
    """測試已知可用的資料表"""
    print("\n✅ 測試已知可用的資料表...")
    
    # 根據之前測試，這些是確實可用的
    working_tables = [
        'financial_statement:營業利益',
        'financial_statement:稅前淨利',
        'financial_statement:營業成本',
        'financial_statement:營業費用',
        'financial_statement:流動資產',
        'financial_statement:流動負債',
        'financial_statement:現金及約當現金',
        'financial_statement:存貨',
        'financial_statement:利息費用',
        'financial_statement:利息收入',
        'financial_statement:股利收入',
        'financial_statement:所得稅費用',
        'price:收盤價',
        'price:開盤價',
        'price:最高價',
        'price:最低價',
        'price:成交股數'
    ]
    
    for table_name in working_tables:
        try:
            df = data.get(table_name)
            print(f"✅ {table_name}: 可用")
            print(f"   資料形狀: {df.shape}")
            print(f"   欄位數量: {len(df.columns)}")
            if '2330' in df.columns:
                recent_data = df['2330'].dropna().tail(1)
                if not recent_data.empty:
                    print(f"   2330 最新資料: {recent_data.iloc[0]}")
        except Exception as e:
            print(f"❌ {table_name}: 錯誤 - {e}")

def search_for_revenue_data():
    """搜尋營收相關的資料"""
    print("\n📊 搜尋營收相關資料...")
    
    # 嘗試不同的營收相關名稱
    revenue_names = [
        'revenue',
        'monthly_revenue',
        'annual_revenue',
        '營收',
        '月營收',
        '年營收',
        'revenue:營收',
        'revenue:月營收',
        'revenue:年營收'
    ]
    
    for name in revenue_names:
        try:
            df = data.get(name)
            print(f"✅ 找到營收資料: {name}")
            print(f"   資料形狀: {df.shape}")
            if '2330' in df.columns:
                recent_data = df['2330'].dropna().tail(1)
                if not recent_data.empty:
                    print(f"   2330 最新營收: {recent_data.iloc[0]}")
        except Exception as e:
            print(f"❌ {name}: 不可用")

def search_for_growth_data():
    """搜尋成長率相關的資料"""
    print("\n📈 搜尋成長率相關資料...")
    
    # 嘗試不同的成長率名稱
    growth_names = [
        'revenue_qoq',
        'revenue_yoy',
        'eps_qoq',
        'eps_yoy',
        '營收季增率',
        '營收年增率',
        '每股盈餘季增率',
        '每股盈餘年增率',
        'revenue:營收季增率',
        'revenue:營收年增率',
        'eps:每股盈餘季增率',
        'eps:每股盈餘年增率'
    ]
    
    for name in growth_names:
        try:
            df = data.get(name)
            print(f"✅ 找到成長率資料: {name}")
            print(f"   資料形狀: {df.shape}")
            if '2330' in df.columns:
                recent_data = df['2330'].dropna().tail(1)
                if not recent_data.empty:
                    print(f"   2330 最新成長率: {recent_data.iloc[0]}")
        except Exception as e:
            print(f"❌ {name}: 不可用")

if __name__ == "__main__":
    print("🚀 開始探索 FinLab 資料庫實際結構...")
    
    # 測試登入
    if not test_finlab_login():
        exit(1)
    
    # 探索資料庫結構
    explore_finlab_database()
    
    # 測試已知可用的表格
    test_known_working_tables()
    
    # 搜尋特定資料
    search_for_revenue_data()
    search_for_growth_data()
    
    print("\n✅ 探索完成")


