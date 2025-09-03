#!/usr/bin/env python3
"""
為 Google Sheets 貼文紀錄表添加 KOL 設定欄位
包括：發文類型、文章長度、KOL 權重設定參數等
"""

import os
import sys
import json
from datetime import datetime
from typing import List, Dict, Any

# 添加 src 目錄到 Python 路徑
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.clients.google.sheets_client import GoogleSheetsClient

def add_kol_settings_columns():
    """為貼文紀錄表添加 KOL 設定欄位"""
    
    print("=" * 60)
    print("📊 為貼文紀錄表添加 KOL 設定欄位")
    print("=" * 60)
    
    try:
        # 初始化 Google Sheets 客戶端
        credentials_file = "credentials/google-service-account.json"
        spreadsheet_id = "148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LikN2s"
        sheets_client = GoogleSheetsClient(credentials_file, spreadsheet_id)
        
        # 讀取當前的貼文紀錄表
        print("\n📋 讀取當前貼文紀錄表結構...")
        existing_data = sheets_client.read_sheet('貼文記錄表', 'A:R')
        
        if not existing_data:
            print("❌ 無法讀取貼文紀錄表數據")
            return False
        
        headers = existing_data[0]
        print(f"✅ 當前欄位數量: {len(headers)}")
        print(f"📋 當前欄位: {headers}")
        
        # 定義新的欄位
        new_columns = [
            "發文類型",           # 疑問/發表觀點
            "文章長度",           # 短/中/長
            "KOL權重設定",        # JSON格式的權重參數
            "內容生成時間",        # 內容生成的時間戳記
            "KOL設定版本"         # KOL設定的版本號
        ]
        
        # 檢查是否已經存在這些欄位
        existing_headers = [h.strip() for h in headers]
        missing_columns = []
        
        for col in new_columns:
            if col not in existing_headers:
                missing_columns.append(col)
        
        if not missing_columns:
            print("✅ 所有 KOL 設定欄位已存在")
            return True
        
        print(f"\n➕ 需要添加的欄位: {missing_columns}")
        
        # 準備新的標題行
        new_headers = headers + missing_columns
        print(f"📋 新的欄位結構 ({len(new_headers)} 欄):")
        for i, header in enumerate(new_headers, 1):
            print(f"   {i:2d}. {header}")
        
        # 更新標題行
        print(f"\n📝 更新標題行...")
        sheets_client.write_sheet('貼文記錄表', [new_headers], 'A1')
        print("✅ 標題行更新完成")
        
        # 為現有記錄添加空值
        if len(existing_data) > 1:
            print(f"\n📝 為現有 {len(existing_data)-1} 筆記錄添加空值...")
            
            for i, row in enumerate(existing_data[1:], start=2):
                # 為每行添加空值
                new_row = row + [''] * len(missing_columns)
                
                # 寫入更新後的行
                range_name = f'A{i}:{chr(ord("A") + len(new_headers) - 1)}{i}'
                sheets_client.write_sheet('貼文記錄表', [new_row], range_name)
            
            print("✅ 現有記錄更新完成")
        
        # 創建欄位說明
        column_descriptions = {
            "發文類型": "記錄該貼文的發文類型：疑問型(question) 或 發表觀點型(opinion)",
            "文章長度": "記錄該貼文的內容長度：短(short: 50-100字) 或 中(medium: 200-300字) 或 長(long: 400-500字)",
            "KOL權重設定": "記錄生成該貼文時 KOL 的權重設定參數，JSON 格式",
            "內容生成時間": "記錄內容生成的時間戳記",
            "KOL設定版本": "記錄生成該貼文時使用的 KOL 設定版本號"
        }
        
        print(f"\n📋 新增欄位說明:")
        for col, desc in column_descriptions.items():
            print(f"   • {col}: {desc}")
        
        # 驗證更新結果
        print(f"\n🔍 驗證更新結果...")
        updated_data = sheets_client.read_sheet('貼文記錄表', f'A1:{chr(ord("A") + len(new_headers) - 1)}1')
        
        if updated_data and len(updated_data[0]) == len(new_headers):
            print("✅ 欄位添加成功")
            print(f"📊 更新後的欄位結構:")
            for i, header in enumerate(updated_data[0], 1):
                print(f"   {i:2d}. {header}")
        else:
            print("❌ 欄位添加失敗")
            return False
        
        print("\n" + "=" * 60)
        print("✅ KOL 設定欄位添加完成")
        print("=" * 60)
        
        print("\n📋 更新摘要:")
        print(f"1. ✅ 添加了 {len(missing_columns)} 個新欄位")
        print("2. ✅ 更新了標題行")
        print("3. ✅ 為現有記錄添加了空值")
        print("4. ✅ 驗證了更新結果")
        
        print("\n🎯 下一步:")
        print("1. 更新內容生成服務，在生成內容時記錄這些設定")
        print("2. 更新 Dashboard 顯示這些新欄位")
        print("3. 更新發文服務，在發文時記錄這些設定")
        
        return True
        
    except Exception as e:
        print(f"❌ 添加欄位時發生錯誤: {e}")
        return False

def create_sample_kol_settings():
    """創建範例 KOL 權重設定"""
    
    sample_settings = {
        "post_types": {
            "question": {
                "style": "疑問型",
                "weight": 0.3,
                "description": "以疑問句為主，引起討論"
            },
            "opinion": {
                "style": "發表觀點型", 
                "weight": 0.7,
                "description": "發表專業觀點和分析"
            }
        },
        "content_lengths": {
            "short": {
                "weight": 0.2,
                "description": "50-100字，簡潔有力"
            },
            "medium": {
                "weight": 0.6,
                "description": "200-300字，適中長度"
            },
            "long": {
                "weight": 0.2,
                "description": "400-500字，深度分析"
            }
        },
        "version": "1.0",
        "last_updated": datetime.now().isoformat()
    }
    
    return json.dumps(sample_settings, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    success = add_kol_settings_columns()
    
    if success:
        print(f"\n📝 範例 KOL 權重設定:")
        print(create_sample_kol_settings())
