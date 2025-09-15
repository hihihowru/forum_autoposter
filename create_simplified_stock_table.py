#!/usr/bin/env python3
"""
創建簡化的股票資訊表
只包含: stock_id, 公司簡稱, 產業類別, 普通股每股面額, 已發行普通股數或TDR原發行股數, 實收資本額(元)
"""
import os
import pandas as pd
import finlab
from finlab import data
import json

# 從環境變數獲取 API 金鑰
finlab.login(os.getenv("FINLAB_API_KEY"))

try:
    print('開始創建簡化的股票資訊表...')
    
    # 獲取 company_basic_info 資料
    company_data = data.get('company_basic_info')
    
    if company_data is not None and not company_data.empty:
        print(f'原始資料: {len(company_data)} 家公司')
        
        # 選擇需要的欄位
        selected_columns = [
            'stock_id',
            '公司簡稱', 
            '產業類別',
            '普通股每股面額',
            '已發行普通股數或TDR原發行股數',
            '實收資本額(元)'
        ]
        
        # 創建簡化的資料表
        simplified_data = company_data[selected_columns].copy()
        
        # 重新命名欄位為英文，方便後續使用
        simplified_data.columns = [
            'stock_id',
            'company_short_name',
            'industry_category', 
            'par_value_per_share',
            'issued_common_shares',
            'paid_in_capital'
        ]
        
        # 清理資料
        simplified_data = simplified_data.dropna(subset=['stock_id', 'company_short_name'])
        
        print(f'簡化後資料: {len(simplified_data)} 家公司')
        
        # 儲存為 CSV
        csv_filename = 'stock_basic_info.csv'
        simplified_data.to_csv(csv_filename, index=False, encoding='utf-8')
        print(f'✅ 已儲存為 CSV: {csv_filename}')
        
        # 儲存為 JSON
        json_filename = 'stock_basic_info.json'
        simplified_data.to_json(json_filename, orient='records', force_ascii=False, indent=2)
        print(f'✅ 已儲存為 JSON: {json_filename}')
        
        # 顯示前10筆資料
        print('\n=== 前10筆資料預覽 ===')
        print(simplified_data.head(10).to_string(index=False))
        
        # 顯示統計資訊
        print(f'\n=== 統計資訊 ===')
        print(f'總公司數: {len(simplified_data)}')
        print(f'產業類別數: {simplified_data["industry_category"].nunique()}')
        
        print('\n=== 產業分布 (前10個) ===')
        industry_counts = simplified_data['industry_category'].value_counts().head(10)
        for industry, count in industry_counts.items():
            print(f'{industry}: {count} 家')
        
        # 檢查特定股票
        print('\n=== 特定股票檢查 ===')
        test_stocks = ['2330', '2454', '2317', '2881', '2882']
        for stock_id in test_stocks:
            stock_info = simplified_data[simplified_data['stock_id'] == stock_id]
            if not stock_info.empty:
                row = stock_info.iloc[0]
                print(f'{stock_id}: {row["company_short_name"]} - {row["industry_category"]}')
            else:
                print(f'{stock_id}: 未找到')
        
        # 創建股票代號到公司名稱的對應字典
        stock_mapping = {}
        for _, row in simplified_data.iterrows():
            stock_mapping[row['stock_id']] = {
                'company_name': row['company_short_name'],
                'industry': row['industry_category'],
                'par_value': row['par_value_per_share'],
                'issued_shares': row['issued_common_shares'],
                'capital': row['paid_in_capital']
            }
        
        # 儲存對應字典
        mapping_filename = 'stock_mapping.json'
        with open(mapping_filename, 'w', encoding='utf-8') as f:
            json.dump(stock_mapping, f, ensure_ascii=False, indent=2)
        print(f'✅ 已儲存股票對應字典: {mapping_filename}')
        
        print('\n🎉 簡化股票資訊表創建完成！')
        
    else:
        print('❌ 無法獲取 company_basic_info 資料')
        
except Exception as e:
    print(f'❌ 錯誤: {e}')
    import traceback
    traceback.print_exc()


