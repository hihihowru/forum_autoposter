#!/usr/bin/env python3
"""
添加 articleid 欄位到貼文記錄表
"""

import sys
import os

# 添加項目根目錄到 Python 路徑
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
sys.path.append(os.path.join(project_root, 'src'))

from src.clients.google.sheets_client import GoogleSheetsClient

def main():
    print("📋 添加 articleid 欄位:")
    print("-----------------------------------------")
    print("---------------------------------------")
    print()
    
    # 初始化 Google Sheets 客戶端
    sheets_client = GoogleSheetsClient(
        credentials_file="credentials/google-service-account.json",
        spreadsheet_id="148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LikN2s"
    )
    
    try:
        # 讀取貼文記錄表
        post_data = sheets_client.read_sheet("貼文記錄表")
        
        if len(post_data) <= 1:
            print("❌ 沒有找到貼文數據")
            return
        
        headers = post_data[0]
        print(f"📊 當前欄位數量: {len(headers)}")
        
        # 檢查是否已有 articleid 欄位
        if "articleid" in headers:
            print("✅ articleid 欄位已存在")
            return
        
        # 在 body parameter 後面添加 articleid 欄位
        new_headers = headers.copy()
        new_headers.append("articleid")
        
        print(f"📊 新欄位數量: {len(new_headers)}")
        print(f"📋 新增欄位: articleid")
        
        # 更新標題行
        sheets_client.write_sheet("貼文記錄表", [new_headers], "A1:AN1")
        
        # 為現有數據添加空值
        for i, row in enumerate(post_data[1:], 2):
            new_row = row.copy()
            new_row.append("")  # 為 articleid 添加空值
            range_name = f"A{i}:AN{i}"
            sheets_client.write_sheet("貼文記錄表", [new_row], range_name)
        
        print("✅ 成功添加 articleid 欄位")
        
    except Exception as e:
        print(f"❌ 添加失敗: {e}")

if __name__ == "__main__":
    main()
