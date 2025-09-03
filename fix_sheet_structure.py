#!/usr/bin/env python3
"""
重新修復Google Sheets欄位結構
"""

from src.clients.google.sheets_client import GoogleSheetsClient

def fix_sheet_structure():
    """修復貼文記錄表的欄位結構"""
    sheets_client = GoogleSheetsClient(
        "./credentials/google-service-account.json",
        "148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LikN2s"
    )
    
    # 正確的欄位標題（12個欄位）
    correct_headers = [
        "貼文ID", "KOL Serial", "KOL 暱稱", "股票名稱", "股票代號", "話題ID", 
        "平台發文ID", "平台發文URL", "生成標題", "生成內容", "commodity_tags", "發文狀態"
    ]
    
    try:
        # 清空整個工作表並重新寫入正確的標題
        sheets_client.write_sheet('貼文記錄表', [correct_headers])
        print("✅ 已重新修復欄位結構")
        
        # 讀取確認
        data = sheets_client.read_sheet('貼文記錄表')
        print(f"📊 當前總行數: {len(data)}")
        print(f"📋 欄位數: {len(data[0]) if data else 0}")
        
        if data:
            print("✅ 欄位標題:")
            for i, header in enumerate(data[0]):
                print(f"  {i+1}. {header}")
            
    except Exception as e:
        print(f"❌ 修復欄位結構失敗: {e}")

if __name__ == "__main__":
    fix_sheet_structure()
