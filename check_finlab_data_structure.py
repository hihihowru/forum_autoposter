#!/usr/bin/env python3
"""
檢查 FinLab 資料表的正確調用方式
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

def check_data_table_structure():
    """檢查資料表結構"""
    print("\n🔍 檢查資料表結構...")
    
    # 嘗試不同的調用方式
    table_names = [
        'monthly_revenue',
        'fundamental_features',
        'financial_statement:每股盈餘',
        'financial_statement:營業利益'
    ]
    
    for table_name in table_names:
        try:
            print(f"\n嘗試取得: {table_name}")
            df = data.get(table_name)
            print(f"✅ 成功取得 {table_name}")
            print(f"   資料形狀: {df.shape}")
            print(f"   欄位數量: {len(df.columns)}")
            print(f"   索引類型: {type(df.index)}")
            print(f"   前5個索引: {df.index[:5].tolist()}")
            
            if len(df.columns) > 0:
                print(f"   前5個欄位: {df.columns[:5].tolist()}")
                
                # 檢查是否有 2330
                if '2330' in df.columns:
                    print(f"   ✅ 包含 2330")
                    recent_data = df['2330'].dropna().tail(1)
                    if not recent_data.empty:
                        print(f"   最新資料: {recent_data.iloc[0]}")
                        print(f"   資料類型: {type(recent_data.iloc[0])}")
                else:
                    print(f"   ❌ 不包含 2330")
                    
        except Exception as e:
            print(f"❌ 取得 {table_name} 失敗: {e}")

def test_eps_data_correctly():
    """正確測試每股盈餘資料"""
    print("\n💰 正確測試每股盈餘資料...")
    
    try:
        eps_df = data.get('financial_statement:每股盈餘')
        
        if '2330' in eps_df.columns:
            recent_data = eps_df['2330'].dropna().tail(3)
            print(f"✅ 2330 每股盈餘資料:")
            for i, (date, value) in enumerate(recent_data.items()):
                # 檢查日期格式
                if hasattr(date, 'strftime'):
                    date_str = date.strftime('%Y-%m')
                else:
                    date_str = str(date)
                print(f"   {date_str}: {value:.2f}")
        else:
            print("❌ 2330 不在每股盈餘資料中")
            
    except Exception as e:
        print(f"❌ 每股盈餘資料取得失敗: {e}")

def search_and_test():
    """搜尋並測試資料表"""
    print("\n🔍 搜尋並測試資料表...")
    
    # 搜尋營收相關資料
    try:
        print("搜尋 '營收' 相關資料...")
        results = data.search('營收')
        print(f"搜尋結果: {results}")
        
        # 嘗試從搜尋結果中取得資料
        for result in results:
            table_name = result['name']
            print(f"\n嘗試取得: {table_name}")
            try:
                df = data.get(table_name)
                print(f"✅ 成功取得 {table_name}")
                print(f"   資料形狀: {df.shape}")
                if '2330' in df.columns:
                    print(f"   ✅ 包含 2330")
                else:
                    print(f"   ❌ 不包含 2330")
            except Exception as e:
                print(f"❌ 取得 {table_name} 失敗: {e}")
                
    except Exception as e:
        print(f"搜尋失敗: {e}")

if __name__ == "__main__":
    print("🚀 檢查 FinLab 資料表的正確調用方式...")
    
    # 測試登入
    if not test_finlab_login():
        exit(1)
    
    # 檢查資料表結構
    check_data_table_structure()
    
    # 正確測試每股盈餘資料
    test_eps_data_correctly()
    
    # 搜尋並測試
    search_and_test()
    
    print("\n✅ 檢查完成")


