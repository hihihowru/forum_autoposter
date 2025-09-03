#!/usr/bin/env python3
"""
恢復Google Sheets正確的欄位結構
"""

from src.clients.google.sheets_client import GoogleSheetsClient

def restore_sheet_structure():
    """恢復貼文記錄表的正確欄位結構"""
    sheets_client = GoogleSheetsClient(
        "./credentials/google-service-account.json",
        "148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LikN2s"
    )
    
    # 正確的欄位標題
    correct_headers = [
        "貼文ID", "KOL Serial", "KOL 暱稱", "股票名稱", "股票代號", "話題ID", 
        "平台發文ID", "平台發文URL", "生成標題", "生成內容", "commodity_tags", "發文狀態"
    ]
    
    try:
        # 清空第一行並寫入正確的標題
        sheets_client.write_sheet('貼文記錄表', [correct_headers], range_name='A1:L1')
        print("✅ 已恢復正確的欄位結構")
        
        # 讀取現有數據
        data = sheets_client.read_sheet('貼文記錄表')
        print(f"📊 當前總行數: {len(data)}")
        
        # 顯示前幾行數據
        for i, row in enumerate(data[:5]):
            print(f"第{i+1}行: {row[:6]}...")
            
    except Exception as e:
        print(f"❌ 恢復欄位結構失敗: {e}")

if __name__ == "__main__":
    restore_sheet_structure()
