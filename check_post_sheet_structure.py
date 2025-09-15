#!/usr/bin/env python3
"""
檢查貼文記錄表的欄位結構
"""

import logging
from google.oauth2 import service_account
from googleapiclient.discovery import build

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_post_sheet_structure():
    """檢查貼文記錄表的欄位結構"""
    try:
        # 初始化 Google Sheets 服務
        credentials = service_account.Credentials.from_service_account_file(
            'credentials/google-service-account.json',
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        service = build('sheets', 'v4', credentials=credentials)
        
        spreadsheet_id = os.getenv('GOOGLE_SHEETS_ID')
        
        # 讀取貼文記錄表的標題行
        range_name = '貼文記錄表!A1:Z1'
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=range_name
        ).execute()
        
        headers = result.get('values', [[]])[0]
        logger.info(f"📊 貼文記錄表標題行: {len(headers)} 個欄位")
        
        for i, header in enumerate(headers):
            logger.info(f"   {i+1}. {header}")
        
        # 讀取前幾行數據來檢查實際欄位數
        range_name = '貼文記錄表!A2:Z5'
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=range_name
        ).execute()
        
        values = result.get('values', [])
        if values:
            logger.info(f"📝 第一行數據有 {len(values[0])} 個欄位")
            logger.info(f"📝 第二行數據有 {len(values[1]) if len(values) > 1 else 0} 個欄位")
            logger.info(f"📝 第三行數據有 {len(values[2]) if len(values) > 2 else 0} 個欄位")
            
            # 顯示第一行數據
            if values:
                logger.info("📝 第一行數據內容:")
                for i, value in enumerate(values[0]):
                    logger.info(f"   {i+1}. {value}")
        
        # 檢查 Dashboard API 使用的範圍是否足夠
        dashboard_range = 'A:R'  # Dashboard API 使用的範圍
        logger.info(f"🔍 Dashboard API 使用範圍: {dashboard_range}")
        
        if len(headers) > 18:  # R 是第18列
            logger.warning(f"⚠️ 貼文記錄表有 {len(headers)} 個欄位，但 Dashboard API 只讀取到 R 列")
            logger.warning("⚠️ 這可能導致部分數據無法讀取")
        else:
            logger.info("✅ Dashboard API 的讀取範圍足夠")
            
    except Exception as e:
        logger.error(f"❌ 檢查貼文記錄表結構失敗: {e}")

if __name__ == "__main__":
    check_post_sheet_structure()


