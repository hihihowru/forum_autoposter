#!/usr/bin/env python3
"""
檢查生成標題欄位的內容
"""

import sys
import os

# 添加項目根目錄到 Python 路徑
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
sys.path.append(os.path.join(project_root, 'src'))

from src.clients.google.sheets_client import GoogleSheetsClient

def main():
    print("📋 檢查生成標題欄位:")
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
        sheet_name = "貼文記錄表"
        data = sheets_client.read_sheet(sheet_name)
        
        if len(data) <= 1:
            print("❌ 沒有找到貼文數據")
            return
        
        # 找到標題欄位的索引
        headers = data[0]
        title_index = None
        content_index = None
        
        for i, header in enumerate(headers):
            if header == "生成標題":
                title_index = i
            elif header == "生成內容":
                content_index = i
        
        if title_index is None:
            print("❌ 找不到 '生成標題' 欄位")
            return
        
        if content_index is None:
            print("❌ 找不到 '生成內容' 欄位")
            return
        
        print(f"📊 標題欄位索引: {title_index}")
        print(f"📊 內容欄位索引: {content_index}")
        print()
        
        # 檢查每篇貼文
        for i, row in enumerate(data[1:], 1):
            if len(row) <= max(title_index, content_index):
                continue
                
            post_id = row[0] if len(row) > 0 else "未知"
            kol_name = row[2] if len(row) > 2 else "未知"
            title = row[title_index] if len(row) > title_index else "無標題"
            content = row[content_index] if len(row) > content_index else "無內容"
            
            print(f"【第 {i} 篇貼文】")
            print(f"  📝 Post ID: {post_id}")
            print(f"  👤 KOL: {kol_name}")
            print(f"  📋 生成標題: {title}")
            print(f"  📄 生成內容: {content[:100]}...")
            print("----------------------------------------")
            print()
            
    except Exception as e:
        print(f"❌ 檢查失敗: {e}")

if __name__ == "__main__":
    main()
























