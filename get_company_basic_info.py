#!/usr/bin/env python3
"""
透過 Finlab API 取得公司基本資訊表
包含公司名稱及相應代號
"""

import os
import pandas as pd
import finlab
from finlab import data
import json
from datetime import datetime

def get_company_basic_info():
    """取得公司基本資訊表"""
    try:
        # 登入 Finlab API
        api_key = os.getenv("FINLAB_API_KEY")
        if not api_key:
            print("❌ 錯誤：請設定 FINLAB_API_KEY 環境變數")
            return None
        
        print("🔐 正在登入 Finlab API...")
        finlab.login(api_key)
        print("✅ Finlab API 登入成功")
        
        # 取得公司基本資訊
        print("📊 正在取得公司基本資訊...")
        company_info = data.get('company_basic_info')
        
        if company_info is None or company_info.empty:
            print("❌ 無法取得公司基本資訊數據")
            return None
        
        print(f"✅ 成功取得 {len(company_info)} 筆公司資料")
        
        # 顯示數據結構
        print("\n📋 數據結構預覽：")
        print(f"欄位: {list(company_info.columns)}")
        print(f"形狀: {company_info.shape}")
        
        # 顯示前幾筆資料
        print("\n📄 前 10 筆資料預覽：")
        print(company_info.head(10))
        
        # 檢查是否有公司名稱和代號欄位
        print("\n🔍 檢查欄位內容：")
        for col in company_info.columns:
            print(f"  {col}: {company_info[col].dtype}")
            if company_info[col].dtype == 'object':
                print(f"    範例值: {company_info[col].dropna().iloc[0] if not company_info[col].dropna().empty else 'N/A'}")
        
        # 儲存為 CSV
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f"company_basic_info_{timestamp}.csv"
        company_info.to_csv(csv_filename, index=True, encoding='utf-8-sig')
        print(f"\n💾 資料已儲存至: {csv_filename}")
        
        # 儲存為 JSON
        json_filename = f"company_basic_info_{timestamp}.json"
        company_info.to_json(json_filename, orient='index', force_ascii=False, indent=2)
        print(f"💾 資料已儲存至: {json_filename}")
        
        return company_info
        
    except Exception as e:
        print(f"❌ 錯誤：{str(e)}")
        return None

def analyze_company_data(df):
    """分析公司數據"""
    if df is None:
        return
    
    print("\n📈 數據分析：")
    print(f"總公司數量: {len(df)}")
    
    # 檢查是否有重複的公司代號
    if 'stock_id' in df.columns:
        duplicates = df['stock_id'].duplicated().sum()
        print(f"重複的公司代號: {duplicates}")
    
    # 檢查是否有重複的公司名稱
    if 'company_name' in df.columns:
        duplicates = df['company_name'].duplicated().sum()
        print(f"重複的公司名稱: {duplicates}")
    
    # 顯示數據類型統計
    print("\n📊 數據類型統計：")
    print(df.dtypes.value_counts())

if __name__ == "__main__":
    print("🚀 開始取得公司基本資訊...")
    company_data = get_company_basic_info()
    
    if company_data is not None:
        analyze_company_data(company_data)
        print("\n✅ 完成！")
    else:
        print("\n❌ 失敗！")





