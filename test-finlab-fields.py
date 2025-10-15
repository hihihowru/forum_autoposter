#!/usr/bin/env python3
"""
測試 finlab API 的 company_basic_info 欄位
"""
import os
import pandas as pd
import finlab
from finlab import data

# 從環境變數獲取 API 金鑰
finlab.login(os.getenv("FINLAB_API_KEY"))

try:
    print('=== finlab API company_basic_info 欄位資訊 ===')
    
    # 獲取 company_basic_info 資料
    company_data = data.get('company_basic_info')
    
    if company_data is not None and not company_data.empty:
        print(f'總共 {len(company_data)} 家公司')
        print(f'總共 {len(company_data.columns)} 個欄位')
        
        print('\n=== 所有欄位列表 ===')
        for i, col in enumerate(company_data.columns, 1):
            print(f'{i:2d}. {col}')
        
        print('\n=== 台積電(2330)範例資料 ===')
        tsmc_data = company_data[company_data['stock_id'] == '2330']
        if not tsmc_data.empty:
            row = tsmc_data.iloc[0]
            print(f'股票代號: {row["stock_id"]}')
            print(f'公司簡稱: {row["公司簡稱"]}')
            print(f'公司名稱: {row["公司名稱"]}')
            print(f'產業類別: {row["產業類別"]}')
            print(f'董事長: {row["董事長"]}')
            print(f'總經理: {row["總經理"]}')
            print(f'上市日期: {row["上市日期"]}')
            print(f'市場別: {row["市場別"]}')
            print(f'住址: {row["住址"]}')
            print(f'總機電話: {row["總機電話"]}')
            print(f'公司網址: {row["公司網址"]}')
        
        print('\n=== 聯發科(2454)範例資料 ===')
        mtk_data = company_data[company_data['stock_id'] == '2454']
        if not mtk_data.empty:
            row = mtk_data.iloc[0]
            print(f'股票代號: {row["stock_id"]}')
            print(f'公司簡稱: {row["公司簡稱"]}')
            print(f'公司名稱: {row["公司名稱"]}')
            print(f'產業類別: {row["產業類別"]}')
            print(f'董事長: {row["董事長"]}')
            print(f'總經理: {row["總經理"]}')
            print(f'上市日期: {row["上市日期"]}')
            print(f'市場別: {row["市場別"]}')
        
        print('\n=== 產業類別統計 (前10個) ===')
        industry_counts = company_data['產業類別'].value_counts().head(10)
        for industry, count in industry_counts.items():
            print(f'{industry}: {count} 家')
        
        print('\n=== 市場別統計 ===')
        market_counts = company_data['市場別'].value_counts()
        for market, count in market_counts.items():
            print(f'{market}: {count} 家')
            
    else:
        print('無法獲取 company_basic_info 資料')
        
except Exception as e:
    print(f'錯誤: {e}')
    import traceback
    traceback.print_exc()


