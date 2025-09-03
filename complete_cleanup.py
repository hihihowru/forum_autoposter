#!/usr/bin/env python3
"""
完全清理：清空所有舊的貼文記錄，只保留表頭
"""

import os
import sys
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.clients.google.sheets_client import GoogleSheetsClient

def complete_cleanup():
    """完全清理貼文記錄"""
    
    print("🧹 執行完全清理：清空所有舊的貼文記錄...")
    print("=" * 80)
    
    # 初始化 Google Sheets 客戶端
    sheets_client = GoogleSheetsClient(
        credentials_file=os.getenv('GOOGLE_CREDENTIALS_FILE'),
        spreadsheet_id=os.getenv('GOOGLE_SHEETS_ID')
    )
    
    try:
        # 讀取貼文記錄表
        data = sheets_client.read_sheet('貼文記錄表', 'A:R')
        
        if not data or len(data) < 2:
            print("❌ 貼文記錄表為空或格式錯誤")
            return
        
        headers = data[0]
        rows = data[1:]
        
        print(f"📊 總記錄數: {len(rows)}")
        print(f"📋 表頭欄位數: {len(headers)}")
        print()
        
        # 檢查需要清理的記錄
        records_to_clean = []
        
        for i, row in enumerate(rows, 1):
            if len(row) >= 16:  # 確保有足夠的欄位
                post_id = row[0] if len(row) > 0 and row[0] else "N/A"
                kol_serial = row[1] if len(row) > 1 and row[1] else "N/A"
                kol_nickname = row[2] if len(row) > 2 and row[2] else "N/A"
                
                # 檢查是否有實際內容
                if (post_id != "N/A" and post_id.strip()) or \
                   (kol_serial != "N/A" and kol_serial.strip()) or \
                   (kol_nickname != "N/A" and kol_nickname.strip()):
                    records_to_clean.append({
                        'row_index': i + 1,
                        'post_id': post_id,
                        'kol_serial': kol_serial,
                        'kol_nickname': kol_nickname
                    })
        
        if records_to_clean:
            print(f"🧹 發現 {len(records_to_clean)} 條記錄需要清理:")
            print("=" * 80)
            
            for i, record in enumerate(records_to_clean, 1):
                print(f"{i}. 行號 {record['row_index']}: {record['kol_nickname']}")
                print(f"   - 貼文ID: {record['post_id']}")
                print(f"   - KOL Serial: {record['kol_serial']}")
                print()
            
            # 確認清理
            print("⚠️ 警告：這將完全清空所有貼文記錄！")
            confirm = input("確定要繼續嗎？(輸入 'YES' 確認): ").strip()
            
            if confirm == 'YES':
                print("\n🧹 開始執行完全清理...")
                print("=" * 80)
                
                # 清空所有數據行，只保留表頭
                # 從第2行開始清空到最後
                start_row = 2
                end_row = len(data)
                
                # 創建空行數據
                empty_row = [''] * len(headers)
                
                # 清空所有數據行
                for row_num in range(start_row, end_row + 1):
                    range_name = f'A{row_num}:R{row_num}'
                    sheets_client.write_sheet('貼文記錄表', [empty_row], range_name)
                    print(f"✅ 已清空行 {row_num}")
                
                print()
                print("🧹 完全清理完成！")
                print("=" * 80)
                print("📋 清理結果:")
                print(f"  🗑️ 已清空記錄: {len(records_to_clean)} 條")
                print(f"  📝 保留表頭: 1 行")
                print(f"  🔄 準備重新生成: 是")
                print()
                print("💡 下一步:")
                print("1. 運行熱門話題腳本生成新貼文")
                print("2. 檢查新生成的貼文品質")
                print("3. 手動審核後決定是否發布")
                
            else:
                print("❌ 取消清理操作")
        else:
            print("✅ 沒有發現需要清理的記錄")
        
        print()
        print("=" * 80)
        print("✅ 清理檢查完成！")
        
    except Exception as e:
        print(f"❌ 完全清理失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    complete_cleanup()



