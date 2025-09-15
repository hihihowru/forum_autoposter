#!/usr/bin/env python3
"""
檢查 finlab company_basic_info 資料結構
"""
import os
import pandas as pd
import finlab
from finlab import data

# 登入 API 金鑰
finlab.login(os.getenv("FINLAB_API_KEY"))

try:
    print('檢查 finlab company_basic_info 資料結構...')
    
    # 獲取 company_basic_info 資料
    company_data = data.get('company_basic_info')
    
    if company_data is not None and not company_data.empty:
        print(f'資料形狀: {company_data.shape}')
        print(f'欄位名稱: {list(company_data.columns)}')
        print('\n前5筆資料:')
        print(company_data.head())
        
        print('\n資料類型:')
        print(company_data.dtypes)
        
        print('\n檢查是否有非空值:')
        for col in company_data.columns:
            non_null_count = company_data[col].notna().sum()
            print(f'{col}: {non_null_count} 個非空值')
        
        # 檢查特定股票代號
        if '2330' in company_data.index:
            print('\n2330 的資料:')
            print(company_data.loc['2330'])
        else:
            print('\n2330 不在索引中')
            print('前10個索引:')
            print(company_data.index[:10])
            
    else:
        print('無法獲取 company_basic_info 資料')
        
except Exception as e:
    print(f'錯誤: {e}')
    import traceback
    traceback.print_exc()


