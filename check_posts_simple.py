#!/usr/bin/env python3
"""
簡單檢查貼文記錄 - 不依賴Docker
"""

import os
import sys
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

def check_posts_simple():
    """簡單檢查貼文記錄"""
    
    print("🔍 檢查貼文記錄...")
    print("=" * 60)
    
    # 檢查環境變數
    google_credentials = os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials/google-service-account.json')
    google_sheets_id = os.getenv('GOOGLE_SHEETS_ID', '148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LikN2s')
    
    print(f"📋 Google Sheets ID: {google_sheets_id}")
    print(f"🔑 認證檔案: {google_credentials}")
    print()
    
    # 檢查認證檔案是否存在
    if not os.path.exists(google_credentials):
        print(f"❌ 認證檔案不存在: {google_credentials}")
        print("請檢查環境變數 GOOGLE_CREDENTIALS_FILE")
        return
    
    try:
        # 嘗試導入Google Sheets相關模組
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        
        print("✅ Google API 模組載入成功")
        
        # 初始化認證
        credentials = service_account.Credentials.from_service_account_file(
            google_credentials,
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        service = build('sheets', 'v4', credentials=credentials)
        
        print("✅ Google Sheets API 認證成功")
        
        # 讀取貼文記錄表
        print("📖 讀取貼文記錄表...")
        range_name = '貼文記錄表!A2:Z1000'  # 讀取前1000行
        result = service.spreadsheets().values().get(
            spreadsheetId=google_sheets_id,
            range=range_name
        ).execute()
        
        values = result.get('values', [])
        
        if not values:
            print("⚠️ 貼文記錄表為空")
            return
        
        print(f"📊 找到 {len(values)} 筆貼文記錄")
        print()
        
        # 統計不同狀態的貼文
        status_count = {}
        kol_count = {}
        
        for i, row in enumerate(values):
            if len(row) >= 12:  # 確保有足夠的欄位
                post_id = row[0] if row[0] else f"空ID_{i}"
                kol_nickname = row[2] if len(row) > 2 else "未知KOL"
                status = row[11] if len(row) > 11 else "未知狀態"
                
                # 統計狀態
                status_count[status] = status_count.get(status, 0) + 1
                
                # 統計KOL
                kol_count[kol_nickname] = kol_count.get(kol_nickname, 0) + 1
        
        # 顯示統計結果
        print("📈 貼文狀態統計:")
        for status, count in sorted(status_count.items()):
            print(f"  {status}: {count} 筆")
        
        print()
        print("👥 KOL 發文統計 (前10名):")
        sorted_kols = sorted(kol_count.items(), key=lambda x: x[1], reverse=True)
        for kol, count in sorted_kols[:10]:
            print(f"  {kol}: {count} 筆")
        
        print()
        print("🔍 最近5筆貼文:")
        for i, row in enumerate(values[:5]):
            if len(row) >= 12:
                post_id = row[0] if row[0] else "N/A"
                kol_nickname = row[2] if len(row) > 2 else "N/A"
                status = row[11] if len(row) > 11 else "N/A"
                title = row[8] if len(row) > 8 else "N/A"
                content = row[10] if len(row) > 10 else "N/A"
                
                print(f"  【第 {i+1} 筆】")
                print(f"    ID: {post_id}")
                print(f"    KOL: {kol_nickname}")
                print(f"    狀態: {status}")
                print(f"    標題: {title[:50]}..." if len(title) > 50 else f"    標題: {title}")
                print(f"    內容: {content[:100]}..." if len(content) > 100 else f"    內容: {content}")
                print()
        
        # 檢查是否有46則以上的貼文
        total_posts = len(values)
        print(f"🎯 總貼文數量: {total_posts}")
        
        if total_posts >= 46:
            print("✅ 恭喜！你有46則以上的貼文生成紀錄")
        else:
            print(f"⚠️ 目前只有 {total_posts} 則貼文，少於46則")
        
        print()
        print("=" * 60)
        print("✅ 檢查完成！")
        
    except ImportError as e:
        print(f"❌ 缺少必要的Python套件: {e}")
        print("請執行: pip install google-api-python-client google-auth-oauthlib")
        
    except Exception as e:
        print(f"❌ 檢查失敗: {e}")
        print("可能的原因:")
        print("1. Google Sheets API 認證失敗")
        print("2. 網路連接問題")
        print("3. Google Sheets 權限問題")

if __name__ == "__main__":
    check_posts_simple()
