#!/usr/bin/env python3
"""
使用 FinLab 的 search 功能來找到正確的資料表
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

def search_finlab_data():
    """使用 FinLab 的 search 功能搜尋資料"""
    print("\n🔍 使用 FinLab search 功能...")
    
    # 搜尋關鍵字
    search_keywords = [
        '營收',
        'revenue',
        '營收成長',
        '營收成長率',
        '營收季增',
        '營收年增',
        '每股盈餘',
        'eps',
        '每股盈餘成長',
        '每股盈餘季增',
        '每股盈餘年增',
        '成長率',
        '季增率',
        '年增率',
        'qoq',
        'yoy'
    ]
    
    for keyword in search_keywords:
        try:
            print(f"\n搜尋關鍵字: {keyword}")
            results = data.search(keyword)
            print(f"搜尋結果: {results}")
        except Exception as e:
            print(f"搜尋 {keyword} 時發生錯誤: {e}")

def test_calculated_revenue():
    """測試從財務報表計算營收"""
    print("\n📊 測試從財務報表計算營收...")
    
    try:
        # 取得營業成本和營業利益
        cost_df = data.get('financial_statement:營業成本')
        profit_df = data.get('financial_statement:營業利益')
        
        if '2330' in cost_df.columns and '2330' in profit_df.columns:
            # 營收 = 營業成本 + 營業利益
            cost_2330 = cost_df['2330'].dropna().tail(1).iloc[0]
            profit_2330 = profit_df['2330'].dropna().tail(1).iloc[0]
            revenue_2330 = cost_2330 + profit_2330
            
            print(f"✅ 計算 2330 營收:")
            print(f"   營業成本: {cost_2330:,.0f}")
            print(f"   營業利益: {profit_2330:,.0f}")
            print(f"   計算營收: {revenue_2330:,.0f}")
            
            # 格式化顯示
            if revenue_2330 >= 100000000:  # 億
                yi = revenue_2330 // 100000000
                wan = (revenue_2330 % 100000000) // 10000
                print(f"   格式化營收: {yi}億{wan}萬")
            
    except Exception as e:
        print(f"計算營收時發生錯誤: {e}")

def test_calculated_ratios():
    """測試計算財務比率"""
    print("\n📈 測試計算財務比率...")
    
    try:
        # 取得基礎資料
        cost_df = data.get('financial_statement:營業成本')
        profit_df = data.get('financial_statement:營業利益')
        expense_df = data.get('financial_statement:營業費用')
        
        if '2330' in cost_df.columns and '2330' in profit_df.columns:
            # 計算毛利率 = 營業利益 / (營業成本 + 營業利益)
            cost_2330 = cost_df['2330'].dropna().tail(1).iloc[0]
            profit_2330 = profit_df['2330'].dropna().tail(1).iloc[0]
            expense_2330 = expense_df['2330'].dropna().tail(1).iloc[0]
            
            revenue_2330 = cost_2330 + profit_2330
            gross_margin = (profit_2330 / revenue_2330) * 100
            operating_margin = (profit_2330 / revenue_2330) * 100
            
            print(f"✅ 計算 2330 財務比率:")
            print(f"   毛利率: {gross_margin:.2f}%")
            print(f"   營業利益率: {operating_margin:.2f}%")
            
    except Exception as e:
        print(f"計算財務比率時發生錯誤: {e}")

def explore_more_financial_data():
    """探索更多財務資料"""
    print("\n📋 探索更多財務資料...")
    
    # 嘗試更多可能的財務資料表
    more_financial_tables = [
        'financial_statement:營業收入',
        'financial_statement:銷貨收入',
        'financial_statement:營收',
        'financial_statement:月營收',
        'financial_statement:年營收',
        'financial_statement:基本每股盈餘',
        'financial_statement:稀釋每股盈餘',
        'financial_statement:每股盈餘',
        'financial_statement:每股盈餘成長率',
        'financial_statement:營收成長率',
        'financial_statement:營收季增率',
        'financial_statement:營收年增率'
    ]
    
    for table_name in more_financial_tables:
        try:
            df = data.get(table_name)
            print(f"✅ {table_name}: 可用")
            if '2330' in df.columns:
                recent_data = df['2330'].dropna().tail(1)
                if not recent_data.empty:
                    print(f"   2330 最新資料: {recent_data.iloc[0]}")
        except Exception as e:
            print(f"❌ {table_name}: 不可用")

if __name__ == "__main__":
    print("🚀 使用 FinLab search 功能探索資料...")
    
    # 測試登入
    if not test_finlab_login():
        exit(1)
    
    # 使用 search 功能
    search_finlab_data()
    
    # 測試計算營收
    test_calculated_revenue()
    
    # 測試計算財務比率
    test_calculated_ratios()
    
    # 探索更多財務資料
    explore_more_financial_data()
    
    print("\n✅ 探索完成")


