#!/usr/bin/env python3
"""
清理互動回饋工作表，只保留真實的互動數據
"""

import sys
import os

# 添加項目根目錄到 Python 路徑
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)
sys.path.append(os.path.join(project_root, 'src'))
sys.path.append(os.path.join(project_root, '..', 'src'))

from clients.google.sheets_client import GoogleSheetsClient

def main():
    print("🧹 清理互動回饋工作表:")
    print("-----------------------------------------")
    print()
    
    # 初始化 Google Sheets 客戶端
    sheets_client = GoogleSheetsClient(
        credentials_file="credentials/google-service-account.json",
        spreadsheet_id="148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LikN2s"
    )
    
    # 要清理的工作表列表
    sheets_to_clean = [
        "互動回饋_1hr",
        "互動回饋_1day", 
        "互動回饋_7days"
    ]
    
    try:
        for sheet_name in sheets_to_clean:
            print(f"📋 清理 {sheet_name} 工作表...")
            
            # 讀取現有數據
            current_data = sheets_client.read_sheet(sheet_name, 'A1:T100')
            
            if not current_data or len(current_data) == 0:
                print(f"⚠️ {sheet_name} 沒有數據，跳過")
                continue
            
            # 保留標題行
            headers = current_data[0]
            cleaned_data = [headers]
            
            # 只保留有 member_id 的數據行（真實數據）
            for row in current_data[1:]:
                if len(row) > 1 and row[1].strip():  # member_id 不為空
                    cleaned_data.append(row)
            
            # 先清空整個工作表
            sheets_client.write_sheet(sheet_name, [headers], 'A1:T1000')
            
            # 再寫入清理後的數據
            if len(cleaned_data) > 1:
                sheets_client.write_sheet(sheet_name, cleaned_data, 'A1:T1000')
            
            print(f"✅ {sheet_name} 已清理，保留 {len(cleaned_data)-1} 條真實數據")
        
        print("\n🎉 所有互動回饋工作表清理完成！")
        print("📊 只保留了有 member_id 的真實互動數據")
        
    except Exception as e:
        print(f"❌ 清理失敗: {e}")

if __name__ == "__main__":
    main()
