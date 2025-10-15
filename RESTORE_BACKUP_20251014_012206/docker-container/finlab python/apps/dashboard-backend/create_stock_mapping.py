#!/usr/bin/env python3
"""
從StockTable.xls創建股票名稱映射字典
"""

import pandas as pd
import json
import os

def create_stock_mapping():
    """從Excel文件創建股票名稱映射"""
    
    # Excel文件路徑
    excel_file = '/Users/williamchen/Documents/n8n-migration-project/StockTable.xls'
    
    if not os.path.exists(excel_file):
        print(f"Excel文件不存在: {excel_file}")
        return
    
    try:
        # 讀取HTML文件（實際上是HTML格式的Excel文件）
        print("正在讀取HTML格式的股票表格...")
        df = pd.read_html(excel_file, encoding='big5')[0]  # 讀取第一個表格
        
        print(f"Excel文件包含 {len(df)} 行數據")
        print("列名:", df.columns.tolist())
        
        # 顯示前幾行數據來了解結構
        print("\n前5行數據:")
        print(df.head())
        
        # 嘗試找到股票代號和名稱的列
        # 通常股票代號是數字，股票名稱是中文
        stock_mapping = {}
        
        for index, row in df.iterrows():
            # 嘗試不同的列組合
            for col in df.columns:
                if pd.isna(row[col]):
                    continue
                    
                # 檢查是否為股票代號（4位數字）
                if str(row[col]).isdigit() and len(str(row[col])) == 4:
                    stock_code = str(row[col])
                    
                    # 尋找對應的股票名稱（在同一行的其他列中）
                    for name_col in df.columns:
                        if name_col != col and not pd.isna(row[name_col]):
                            stock_name = str(row[name_col]).strip()
                            # 檢查是否為中文名稱
                            if any('\u4e00' <= char <= '\u9fff' for char in stock_name):
                                stock_mapping[stock_code] = stock_name
                                break
        
        print(f"\n成功創建股票映射，共 {len(stock_mapping)} 支股票")
        
        # 顯示前10個映射
        print("\n前10個股票映射:")
        for i, (code, name) in enumerate(list(stock_mapping.items())[:10]):
            print(f"{code}: {name}")
        
        # 保存為Python字典格式
        python_dict_file = '/Users/williamchen/Documents/n8n-migration-project/docker-container/finlab python/apps/dashboard-backend/stock_names_mapping.py'
        
        with open(python_dict_file, 'w', encoding='utf-8') as f:
            f.write('"""\n')
            f.write('股票代號對應股票名稱映射字典\n')
            f.write('從StockTable.xls自動生成\n')
            f.write('"""\n\n')
            f.write('STOCK_NAMES = {\n')
            
            # 按股票代號排序
            for code in sorted(stock_mapping.keys()):
                name = stock_mapping[code]
                f.write(f'    "{code}": "{name}",\n')
            
            f.write('}\n')
        
        print(f"\n股票映射已保存到: {python_dict_file}")
        
        # 也保存為JSON格式
        json_file = '/Users/williamchen/Documents/n8n-migration-project/docker-container/finlab python/apps/dashboard-backend/stock_names_mapping.json'
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(stock_mapping, f, ensure_ascii=False, indent=2)
        
        print(f"股票映射JSON已保存到: {json_file}")
        
        return stock_mapping
        
    except Exception as e:
        print(f"處理Excel文件時發生錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_stock_mapping()
