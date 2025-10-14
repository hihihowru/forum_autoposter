#!/usr/bin/env python3
"""
檢查 body parameter 格式
"""

import sys
import os

# 添加項目根目錄到 Python 路徑
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
sys.path.append(os.path.join(project_root, 'src'))

from src.clients.google.sheets_client import GoogleSheetsClient

def main():
    print("📋 檢查 body parameter 格式:")
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
        body_param_index = None
        
        # 查找 body parameter 欄位
        for i, header in enumerate(headers):
            if header == "body parameter":
                body_param_index = i
                break
        
        if body_param_index is None:
            print("❌ 找不到 'body parameter' 欄位")
            return
        
        print(f"📊 body parameter 欄位索引: {body_param_index}")
        print()
        
        # 檢查最近的貼文
        for i, row in enumerate(post_data[1:], 1):
            if len(row) > body_param_index:
                post_id = row[0] if len(row) > 0 else "未知"
                kol_name = row[2] if len(row) > 2 else "未知"
                body_param = row[body_param_index] if len(row) > body_param_index else "無"
                
                print(f"【第 {i} 篇貼文】")
                print(f"  📝 Post ID: {post_id}")
                print(f"  👤 KOL: {kol_name}")
                print(f"  📋 body parameter: {body_param}")
                print("----------------------------------------")
                print()
            
    except Exception as e:
        print(f"❌ 檢查失敗: {e}")

if __name__ == "__main__":
    main()
