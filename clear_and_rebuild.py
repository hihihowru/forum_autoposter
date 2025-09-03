#!/usr/bin/env python3
"""
使用Google Sheets API直接清空並重建工作表
"""

from src.clients.google.sheets_client import GoogleSheetsClient

def clear_and_rebuild_sheet():
    """清空並重建貼文記錄表"""
    sheets_client = GoogleSheetsClient(
        "./credentials/google-service-account.json",
        "148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LikN2s"
    )
    
    try:
        # 先清空整個工作表
        sheets_client.service.spreadsheets().values().clear(
            spreadsheetId=sheets_client.spreadsheet_id,
            range='貼文記錄表'
        ).execute()
        print("✅ 已清空工作表")
        
        # 正確的欄位標題（12個欄位）
        correct_headers = [
            "貼文ID", "KOL Serial", "KOL 暱稱", "股票名稱", "股票代號", "話題ID", 
            "平台發文ID", "平台發文URL", "生成標題", "生成內容", "commodity_tags", "發文狀態"
        ]
        
        # 寫入標題
        sheets_client.write_sheet('貼文記錄表', [correct_headers])
        print("✅ 已寫入欄位標題")
        
        # 讀取確認
        data = sheets_client.read_sheet('貼文記錄表')
        print(f"📊 當前總行數: {len(data)}")
        print(f"📋 欄位數: {len(data[0]) if data else 0}")
        
        if data and len(data[0]) == 12:
            print("✅ 欄位結構正確")
            print("✅ 欄位標題:")
            for i, header in enumerate(data[0]):
                print(f"  {i+1}. {header}")
        else:
            print("❌ 欄位結構仍有問題")
            
    except Exception as e:
        print(f"❌ 清空並重建失敗: {e}")

if __name__ == "__main__":
    clear_and_rebuild_sheet()
