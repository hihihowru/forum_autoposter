#!/usr/bin/env python3
"""
檢查更新後的互動數據
"""

import logging
from google.oauth2 import service_account
from googleapiclient.discovery import build

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_updated_interactions():
    """檢查更新後的互動數據"""
    try:
        # 初始化 Google Sheets 服務
        credentials = service_account.Credentials.from_service_account_file(
            'credentials/google-service-account.json',
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        service = build('sheets', 'v4', credentials=credentials)
        
        spreadsheet_id = os.getenv('GOOGLE_SHEETS_ID')
        
        # 讀取互動回饋即時總表
        range_name = '互動回饋即時總表!A2:T10'  # 讀取前9行數據
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=range_name
        ).execute()
        
        values = result.get('values', [])
        if not values:
            logger.warning("⚠️ 互動回饋即時總表為空")
            return
        
        logger.info(f"📊 找到 {len(values)} 筆互動數據")
        
        # 顯示前幾筆數據
        for i, row in enumerate(values[:5]):  # 顯示前5筆
            if len(row) >= 20:
                logger.info(f"📝 第 {i+1} 筆數據:")
                logger.info(f"   Article ID: {row[0]}")
                logger.info(f"   Member ID: {row[1]}")
                logger.info(f"   Nickname: {row[2]}")
                logger.info(f"   Title: {row[3]}")
                logger.info(f"   Likes: {row[9]}")
                logger.info(f"   Comments: {row[10]}")
                logger.info(f"   Total Interactions: {row[11]}")
                logger.info(f"   Engagement Rate: {row[12]}")
                logger.info(f"   Last Update: {row[8]}")
                logger.info("   " + "="*50)
        
        # 統計資訊
        total_likes = sum(int(row[9]) if len(row) > 9 and row[9].isdigit() else 0 for row in values)
        total_comments = sum(int(row[10]) if len(row) > 10 and row[10].isdigit() else 0 for row in values)
        total_interactions = sum(int(row[11]) if len(row) > 11 and row[11].isdigit() else 0 for row in values)
        
        logger.info(f"📈 統計摘要:")
        logger.info(f"   總讚數: {total_likes}")
        logger.info(f"   總留言數: {total_comments}")
        logger.info(f"   總互動數: {total_interactions}")
        logger.info(f"   平均每篇互動: {total_interactions/len(values):.1f}")
        
    except Exception as e:
        logger.error(f"❌ 檢查互動數據失敗: {e}")

if __name__ == "__main__":
    check_updated_interactions()


