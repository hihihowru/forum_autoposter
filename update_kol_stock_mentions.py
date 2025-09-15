#!/usr/bin/env python3
"""
更新KOL角色紀錄表 - 添加股票提及方式欄位
為KOL角色紀錄表添加股票提及個人化設定
"""

import os
import sys
import time
from typing import List, Dict, Any
from dotenv import load_dotenv

# 添加專案路徑
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from clients.google.sheets_client import GoogleSheetsClient

load_dotenv()

class KOLStockMentionUpdater:
    """KOL股票提及方式更新器"""
    
    def __init__(self):
        self.sheets_client = GoogleSheetsClient(
            credentials_file='./credentials/google-service-account.json',
            spreadsheet_id=os.getenv('GOOGLE_SHEETS_ID')
        )
        
        # 股票提及方式設定
        self.stock_mention_settings = {
            "川川哥": {
                "primary_formats": "金像電,金像電(2368),2368,這檔金像電",
                "secondary_formats": "金像電這檔,2368這支,這支金像電,金像電這支",
                "frequency_weights": "金像電:0.4,金像電(2368):0.2,2368:0.3,這檔金像電:0.1",
                "context_modifiers": "技術分析:這檔金像電,新聞評論:金像電(2368),一般提及:金像電,強調:金像電(2368)"
            },
            "韭割哥": {
                "primary_formats": "金像電,金像電這檔,這檔金像電,2368",
                "secondary_formats": "金像電(2368),這支金像電,2368這支,金像電這支",
                "frequency_weights": "金像電:0.5,金像電這檔:0.2,這檔金像電:0.2,2368:0.1",
                "context_modifiers": "技術分析:金像電這檔,新聞評論:金像電,一般提及:金像電,強調:金像電(2368)"
            },
            "梅川褲子": {
                "primary_formats": "金像電,2368,金像電(2368),這檔金像電",
                "secondary_formats": "金像電這檔,這支金像電,2368這支,金像電這支",
                "frequency_weights": "金像電:0.3,2368:0.4,金像電(2368):0.2,這檔金像電:0.1",
                "context_modifiers": "技術分析:2368,新聞評論:金像電,一般提及:金像電,強調:金像電(2368)"
            },
            "八卦護城河": {
                "primary_formats": "金像電,金像電(2368),這檔金像電,金像電這檔",
                "secondary_formats": "2368,這支金像電,2368這支,金像電這支",
                "frequency_weights": "金像電:0.4,金像電(2368):0.3,這檔金像電:0.2,金像電這檔:0.1",
                "context_modifiers": "技術分析:金像電,新聞評論:金像電(2368),一般提及:金像電,強調:金像電(2368)"
            },
            "長線韭韭": {
                "primary_formats": "金像電,金像電這檔,這檔金像電,金像電(2368)",
                "secondary_formats": "2368,這支金像電,2368這支,金像電這支",
                "frequency_weights": "金像電:0.5,金像電這檔:0.2,這檔金像電:0.2,金像電(2368):0.1",
                "context_modifiers": "技術分析:金像電這檔,新聞評論:金像電,一般提及:金像電,強調:金像電(2368)"
            },
            "數據獵人": {
                "primary_formats": "金像電(2368),2368,金像電,這檔金像電",
                "secondary_formats": "金像電這檔,這支金像電,2368這支,金像電這支",
                "frequency_weights": "金像電(2368):0.4,2368:0.3,金像電:0.2,這檔金像電:0.1",
                "context_modifiers": "技術分析:2368,新聞評論:金像電(2368),一般提及:金像電(2368),強調:金像電(2368)"
            }
        }
    
    def _get_column_letter(self, index: int) -> str:
        """將數字索引轉換為Excel欄位字母"""
        result = ""
        while index >= 0:
            result = chr(65 + (index % 26)) + result
            index = index // 26 - 1
        return result
    
    def add_stock_mention_columns(self):
        """添加股票提及方式欄位"""
        try:
            print("📋 添加股票提及方式欄位...")
            
            # 讀取現有表頭
            data = self.sheets_client.read_sheet('KOL 角色紀錄表', 'A1:Z1')
            if not data or len(data) < 1:
                print("❌ 無法讀取表頭")
                return False
            
            headers = data[0]
            print(f"當前欄位數: {len(headers)}")
            print(f"當前欄位: {headers}")
            
            # 需要添加的欄位
            new_columns = [
                '股票提及主要格式',
                '股票提及次要格式', 
                '股票提及頻率權重',
                '股票提及上下文修飾'
            ]
            
            # 檢查哪些欄位需要添加
            missing_columns = []
            for col in new_columns:
                if col not in headers:
                    missing_columns.append(col)
            
            if not missing_columns:
                print("✅ 所有股票提及欄位已存在")
                return True
            
            print(f"需要添加的欄位: {missing_columns}")
            
            # 讀取所有數據
            all_data = self.sheets_client.read_sheet('KOL 角色紀錄表', 'A:Z')
            if not all_data:
                print("❌ 無法讀取數據")
                return False
            
            # 為每一行添加空欄位
            updated_data = []
            for row in all_data:
                new_row = row.copy()
                for _ in missing_columns:
                    new_row.append("")
                updated_data.append(new_row)
            
            # 更新表頭
            updated_headers = headers + missing_columns
            updated_data[0] = updated_headers
            
            print(f"更新後欄位數: {len(updated_headers)}")
            print(f"更新後欄位: {updated_headers}")
            
            # 寫回數據 - 使用固定的範圍
            self.sheets_client.write_sheet('KOL 角色紀錄表', [updated_headers], 'A1:AD1')
            print("✅ 表頭更新完成")
            
            # 等待一下讓Google Sheets更新
            time.sleep(2)
            
            return True
            
        except Exception as e:
            print(f"❌ 添加欄位失敗: {e}")
            return False
    
    def update_kol_stock_mentions(self):
        """更新KOL的股票提及方式設定"""
        try:
            print("📝 更新KOL股票提及方式設定...")
            
            # 讀取現有數據 - 使用更大的範圍
            data = self.sheets_client.read_sheet('KOL 角色紀錄表', 'A:AD')
            if not data or len(data) < 2:
                print("❌ 沒有找到KOL數據")
                return False
            
            headers = data[0]
            rows = data[1:]
            
            # 找到股票提及欄位的索引
            stock_mention_indices = {}
            for col in ['股票提及主要格式', '股票提及次要格式', '股票提及頻率權重', '股票提及上下文修飾']:
                if col in headers:
                    stock_mention_indices[col] = headers.index(col)
                else:
                    print(f"⚠️ 找不到欄位: {col}")
                    return False
            
            print(f"股票提及欄位索引: {stock_mention_indices}")
            
            # 更新每個KOL的股票提及設定
            updated_rows = []
            updated_count = 0
            
            for row in rows:
                if len(row) < 2:
                    updated_rows.append(row)
                    continue
                
                kol_nickname = row[1] if len(row) > 1 else ""  # 暱稱在第2列
                
                # 創建新行，確保有足夠的欄位
                new_row = row.copy()
                while len(new_row) < max(stock_mention_indices.values()) + 1:
                    new_row.append("")
                
                # 如果KOL有預設的股票提及設定，則更新
                if kol_nickname in self.stock_mention_settings:
                    settings = self.stock_mention_settings[kol_nickname]
                    
                    for col, value in settings.items():
                        if col in stock_mention_indices:
                            col_index = stock_mention_indices[col]
                            new_row[col_index] = value
                    
                    updated_count += 1
                    print(f"✅ 更新 {kol_nickname} 的股票提及設定")
                
                updated_rows.append(new_row)
            
            # 寫回數據 - 使用固定的範圍
            if updated_rows:
                self.sheets_client.write_sheet('KOL 角色紀錄表', updated_rows, 'A2:AD' + str(len(updated_rows) + 1))
            
            print(f"✅ 更新完成！共更新 {updated_count} 個KOL的股票提及設定")
            return True
            
        except Exception as e:
            print(f"❌ 更新KOL股票提及設定失敗: {e}")
            return False
    
    def verify_updates(self):
        """驗證更新結果"""
        try:
            print("🔍 驗證更新結果...")
            
            # 等待一下讓Google Sheets更新
            time.sleep(2)
            
            # 讀取更新後的數據 - 使用更大的範圍
            data = self.sheets_client.read_sheet('KOL 角色紀錄表', 'A:AD')
            if not data or len(data) < 2:
                print("❌ 無法讀取更新後的數據")
                return False
            
            headers = data[0]
            rows = data[1:]
            
            # 檢查股票提及欄位
            stock_mention_columns = ['股票提及主要格式', '股票提及次要格式', '股票提及頻率權重', '股票提及上下文修飾']
            
            for col in stock_mention_columns:
                if col in headers:
                    index = headers.index(col)
                    print(f"✅ {col} 在位置 {index}")
                else:
                    print(f"❌ {col} 不存在")
                    return False
            
            print("✅ 所有股票提及欄位都存在")
            
            # 檢查KOL設定
            for row in rows:
                if len(row) < 2:
                    continue
                
                kol_nickname = row[1]
                if kol_nickname in self.stock_mention_settings:
                    # 檢查是否有設定值
                    has_settings = False
                    for col in stock_mention_columns:
                        col_index = headers.index(col)
                        if len(row) > col_index and row[col_index]:
                            has_settings = True
                            break
                    
                    if has_settings:
                        print(f"✅ {kol_nickname} 的股票提及設定已更新")
                    else:
                        print(f"⚠️ {kol_nickname} 的股票提及設定為空")
            
            return True
            
        except Exception as e:
            print(f"❌ 驗證失敗: {e}")
            return False
    
    def run_update(self):
        """執行完整的更新流程"""
        print("🚀 開始更新KOL股票提及方式設定")
        print("=" * 60)
        
        # 步驟1: 添加欄位
        if not self.add_stock_mention_columns():
            print("❌ 欄位添加失敗")
            return False
        
        # 步驟2: 更新KOL設定
        if not self.update_kol_stock_mentions():
            print("❌ KOL設定更新失敗")
            return False
        
        # 步驟3: 驗證更新結果
        if not self.verify_updates():
            print("❌ 驗證失敗")
            return False
        
        print("=" * 60)
        print("🎉 KOL股票提及方式設定更新完成！")
        print("📋 已添加以下欄位:")
        print("  - 股票提及主要格式")
        print("  - 股票提及次要格式")
        print("  - 股票提及頻率權重")
        print("  - 股票提及上下文修飾")
        print()
        print("👤 已更新以下KOL的設定:")
        for kol in self.stock_mention_settings.keys():
            print(f"  - {kol}")
        
        return True

def main():
    """主函數"""
    try:
        updater = KOLStockMentionUpdater()
        updater.run_update()
    except Exception as e:
        print(f"❌ 更新過程中發生錯誤: {e}")

if __name__ == "__main__":
    main()
