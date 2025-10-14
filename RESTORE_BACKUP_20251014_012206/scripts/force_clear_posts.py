#!/usr/bin/env python3
"""
強力清理Google Sheets中的現有貼文記錄
"""

import sys
import os

# 添加項目根目錄到Python路徑
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
sys.path.append(os.path.join(project_root, 'src'))

from src.clients.google.sheets_client import GoogleSheetsClient

def main():
    """強力清理Google Sheets中的現有貼文記錄"""
    
    try:
        # 初始化Google Sheets客戶端
        credentials_file = "credentials/google-service-account.json"
        spreadsheet_id = "148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LikN2s"
        sheets_client = GoogleSheetsClient(credentials_file, spreadsheet_id)
        
        # 讀取貼文記錄表
        sheet_name = "貼文記錄表"
        existing_data = sheets_client.read_sheet(sheet_name)
        
        if not existing_data:
            print("❌ 無法讀取Google Sheets")
            return
        
        print(f"📋 當前數據狀態:")
        print(f"  📊 總行數: {len(existing_data)}")
        
        if len(existing_data) < 2:
            print("✅ 沒有數據需要清理")
            return
        
        # 保留標題行，刪除所有數據行
        headers = existing_data[0]
        
        print(f"📋 強力清理現有貼文記錄:")
        print(f"  📊 將刪除 {len(existing_data) - 1} 行數據")
        
        # 方法1: 嘗試清空整個範圍
        try:
            # 清空A1:AM1000範圍
            empty_data = [[''] * 39] * 1000  # 39個欄位，1000行空數據
            sheets_client.write_sheet(sheet_name, empty_data, "A1:AM1000")
            print("  ✅ 方法1: 清空大範圍完成")
        except Exception as e:
            print(f"  ❌ 方法1失敗: {e}")
        
        # 方法2: 重新寫入標題行
        try:
            sheets_client.write_sheet(sheet_name, [headers], "A1:AM1")
            print("  ✅ 方法2: 重新寫入標題行完成")
        except Exception as e:
            print(f"  ❌ 方法2失敗: {e}")
        
        # 驗證清理結果
        print("\n📋 驗證清理結果:")
        try:
            verification_data = sheets_client.read_sheet(sheet_name)
            print(f"  📊 清理後行數: {len(verification_data)}")
            if len(verification_data) == 1:
                print("  ✅ 清理成功！只保留標題行")
            else:
                print(f"  ⚠️ 清理可能不完整，仍有 {len(verification_data) - 1} 行數據")
        except Exception as e:
            print(f"  ❌ 驗證失敗: {e}")
        
    except Exception as e:
        print(f"❌ 清理失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()












