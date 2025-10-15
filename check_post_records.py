#!/usr/bin/env python3
"""
檢查貼文記錄表內容
"""

import logging
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_post_records():
    """檢查貼文記錄表內容"""
    try:
        # 初始化 Google Sheets 服務
        credentials = service_account.Credentials.from_service_account_file(
            'credentials/google-service-account.json',
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        service = build('sheets', 'v4', credentials=credentials)
        
        spreadsheet_id = os.getenv('GOOGLE_SHEETS_ID', '1R_nBesf62hX5dQEr_SDjHrGefAC9nsOo1Kbih79EHKw')
        
        # 讀取貼文記錄表
        range_name = '貼文記錄表!A2:Z100'  # 讀取前100行數據
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=range_name
        ).execute()
        
        values = result.get('values', [])
        if not values:
            logger.warning("⚠️ 貼文記錄表為空")
            return
        
        logger.info(f"📊 貼文記錄表有 {len(values)} 筆記錄")
        
        # 顯示前幾筆數據
        for i, row in enumerate(values[:5]):  # 顯示前5筆
            if len(row) >= 5:
                logger.info(f"📝 第 {i+1} 筆貼文:")
                logger.info(f"   Article ID: {row[0] if len(row) > 0 else 'N/A'}")
                logger.info(f"   Member ID: {row[1] if len(row) > 1 else 'N/A'}")
                logger.info(f"   Nickname: {row[2] if len(row) > 2 else 'N/A'}")
                logger.info(f"   Title: {row[3] if len(row) > 3 else 'N/A'}")
                logger.info(f"   Content: {row[4] if len(row) > 4 else 'N/A'}")
                logger.info("   " + "="*50)
        
        # 檢查是否有發文記錄
        has_posts = any(len(row) > 0 and row[0] for row in values)
        if has_posts:
            logger.info("✅ 貼文記錄表包含發文記錄")
        else:
            logger.warning("⚠️ 貼文記錄表沒有發文記錄")
            
    except Exception as e:
        logger.error(f"❌ 檢查貼文記錄表失敗: {e}")

if __name__ == "__main__":
    check_post_records()


