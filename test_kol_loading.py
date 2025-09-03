#!/usr/bin/env python3
"""
測試 KOL 配置載入
"""

import os
import sys
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.clients.google.sheets_client import GoogleSheetsClient
from src.services.assign.assignment_service import AssignmentService

def test_kol_loading():
    """測試 KOL 配置載入"""
    
    print("=== 測試 KOL 配置載入 ===\n")
    
    # 初始化服務
    sheets_client = GoogleSheetsClient(
        credentials_file=os.getenv('GOOGLE_CREDENTIALS_FILE'),
        spreadsheet_id=os.getenv('GOOGLE_SHEETS_ID')
    )
    
    assignment_service = AssignmentService(sheets_client)
    
    try:
        # 載入 KOL 配置
        print("載入 KOL 配置...")
        assignment_service.load_kol_profiles()
        
        print(f"載入了 {len(assignment_service._kol_profiles)} 個 KOL")
        
        # 顯示 KOL 資訊
        for kol in assignment_service._kol_profiles:
            print(f"  - Serial: {kol.serial}, 暱稱: {kol.nickname}, 狀態: {kol.status}, 啟用: {kol.enabled}")
        
        # 檢查活躍的 KOL
        active_kols = [kol for kol in assignment_service._kol_profiles if kol.enabled and kol.status == 'active']
        print(f"\n活躍的 KOL: {len(active_kols)} 個")
        
        for kol in active_kols:
            print(f"  - {kol.serial}: {kol.nickname} ({kol.persona})")
        
        print("\n✅ KOL 配置載入測試完成！")
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_kol_loading()
