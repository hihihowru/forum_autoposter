#!/usr/bin/env python3
"""
創建簡化的股票資訊表 - 避免重複驗證
"""
import os
import pandas as pd
import json

# 直接使用已經驗證過的 finlab 會話
try:
    import finlab
    from finlab import data
    
    print('使用已驗證的 finlab 會話...')
    
    # 獲取 company_basic_info 資料
    company_data = data.get('company_basic_info')
    
    if company_data is not None and not company_data.empty:
        print(f'✅ 成功獲取資料: {len(company_data)} 家公司')
        
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
        
        # 重新命名欄位為英文
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
        
        print(f'✅ 簡化後資料: {len(simplified_data)} 家公司')
        
        # 儲存為 CSV
        csv_filename = 'stock_basic_info.csv'
        simplified_data.to_csv(csv_filename, index=False, encoding='utf-8')
        print(f'✅ 已儲存為 CSV: {csv_filename}')
        
        # 儲存為 JSON
        json_filename = 'stock_basic_info.json'
        simplified_data.to_json(json_filename, orient='records', force_ascii=False, indent=2)
        print(f'✅ 已儲存為 JSON: {json_filename}')
        
        # 顯示前5筆資料
        print('\n=== 前5筆資料預覽 ===')
        for i, (_, row) in enumerate(simplified_data.head(5).iterrows()):
            print(f'{i+1}. {row["stock_id"]}: {row["company_short_name"]} - {row["industry_category"]}')
        
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
        
        # 顯示特定股票
        print('\n=== 特定股票檢查 ===')
        test_stocks = ['2330', '2454', '2317', '2881', '2882']
        for stock_id in test_stocks:
            if stock_id in stock_mapping:
                info = stock_mapping[stock_id]
                print(f'{stock_id}: {info["company_name"]} - {info["industry"]}')
            else:
                print(f'{stock_id}: 未找到')
        
        print('\n🎉 簡化股票資訊表創建完成！')
        
    else:
        print('❌ 無法獲取 company_basic_info 資料')
        
except Exception as e:
    print(f'❌ 錯誤: {e}')
    print('請確保 finlab 已經登入')


