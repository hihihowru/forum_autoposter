#!/usr/bin/env python3
"""
透過 Finlab API 取得公司基本資訊表 - 簡化版
只包含公司名稱及相應代號
"""

import os
import pandas as pd
import finlab
from finlab import data
import json
from datetime import datetime

def get_company_name_code_mapping():
    """取得公司名稱與代號對應表"""
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
        
        # 提取公司名稱和代號
        company_mapping = company_info[['stock_id', '公司簡稱', '公司名稱', '產業類別']].copy()
        
        # 重新命名欄位
        company_mapping.columns = ['股票代號', '公司簡稱', '公司名稱', '產業類別']
        
        # 移除重複資料
        company_mapping = company_mapping.drop_duplicates(subset=['股票代號'])
        
        print(f"📋 整理後共有 {len(company_mapping)} 筆不重複的公司資料")
        
        # 顯示前幾筆資料
        print("\n📄 前 10 筆資料預覽：")
        print(company_mapping.head(10))
        
        # 儲存為 CSV
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f"company_name_code_mapping_{timestamp}.csv"
        company_mapping.to_csv(csv_filename, index=False, encoding='utf-8-sig')
        print(f"\n💾 資料已儲存至: {csv_filename}")
        
        # 儲存為 JSON
        json_filename = f"company_name_code_mapping_{timestamp}.json"
        company_mapping.to_json(json_filename, orient='records', force_ascii=False, indent=2)
        print(f"💾 資料已儲存至: {json_filename}")
        
        # 創建字典格式的對應表
        name_to_code = {}
        code_to_name = {}
        
        for _, row in company_mapping.iterrows():
            stock_id = str(row['股票代號'])
            short_name = row['公司簡稱']
            full_name = row['公司名稱']
            
            # 公司簡稱 -> 股票代號
            name_to_code[short_name] = stock_id
            # 公司全名 -> 股票代號
            name_to_code[full_name] = stock_id
            
            # 股票代號 -> 公司資訊
            code_to_name[stock_id] = {
                '公司簡稱': short_name,
                '公司名稱': full_name,
                '產業類別': row['產業類別']
            }
        
        # 儲存字典格式
        dict_filename = f"company_mapping_dict_{timestamp}.json"
        with open(dict_filename, 'w', encoding='utf-8') as f:
            json.dump({
                'name_to_code': name_to_code,
                'code_to_name': code_to_name
            }, f, ensure_ascii=False, indent=2)
        print(f"💾 字典對應表已儲存至: {dict_filename}")
        
        return company_mapping
        
    except Exception as e:
        print(f"❌ 錯誤：{str(e)}")
        return None

def search_company(search_term, company_mapping):
    """搜尋公司"""
    if company_mapping is None:
        return
    
    print(f"\n🔍 搜尋包含 '{search_term}' 的公司：")
    
    # 搜尋公司簡稱
    short_name_matches = company_mapping[company_mapping['公司簡稱'].str.contains(search_term, na=False)]
    # 搜尋公司全名
    full_name_matches = company_mapping[company_mapping['公司名稱'].str.contains(search_term, na=False)]
    # 搜尋股票代號
    code_matches = company_mapping[company_mapping['股票代號'].astype(str).str.contains(search_term, na=False)]
    
    # 合併結果並去重
    all_matches = pd.concat([short_name_matches, full_name_matches, code_matches]).drop_duplicates()
    
    if len(all_matches) > 0:
        print(f"找到 {len(all_matches)} 筆符合的資料：")
        print(all_matches)
    else:
        print("未找到符合條件的公司")

if __name__ == "__main__":
    print("🚀 開始取得公司名稱與代號對應表...")
    company_data = get_company_name_code_mapping()
    
    if company_data is not None:
        print("\n✅ 完成！")
        
        # 示範搜尋功能
        search_company("台積電", company_data)
        search_company("2330", company_data)
    else:
        print("\n❌ 失敗！")





