#!/usr/bin/env python3
"""
檢查Google Sheets中的貼文狀態
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# 添加 src 目錄到 Python 路徑
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.clients.google.sheets_client import GoogleSheetsClient

# 載入環境變數
load_dotenv()

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PostStatusChecker:
    """貼文狀態檢查器"""
    
    def __init__(self):
        # 初始化 Google Sheets 客戶端
        self.sheets_client = GoogleSheetsClient(
            credentials_file="./credentials/google-service-account.json",
            spreadsheet_id="148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LikN2s"
        )
    
    async def check_post_status(self):
        """檢查貼文狀態"""
        try:
            # 讀取貼文記錄表
            posts_data = self.sheets_client.read_sheet('貼文記錄表', 'A:AH')
            
            logger.info(f"📊 總貼文數: {len(posts_data) - 1}")  # 減去標題行
            
            status_count = {}
            pending_posts = []
            
            for i, row in enumerate(posts_data[1:], 1):  # 跳過標題行
                if len(row) >= 12:
                    status = row[11] if len(row) > 11 else 'unknown'  # L欄位是Status
                    status_count[status] = status_count.get(status, 0) + 1
                    
                    if status == 'pending':
                        pending_posts.append({
                            'row': i + 1,
                            'post_id': row[0],
                            'kol_nickname': row[2] if len(row) > 2 else '',
                            'stock_name': row[3] if len(row) > 3 else '',
                            'title': row[8] if len(row) > 8 else ''
                        })
            
            # 顯示狀態統計
            logger.info("📈 狀態統計:")
            for status, count in status_count.items():
                logger.info(f"   {status}: {count} 篇")
            
            # 顯示待發布貼文
            if pending_posts:
                logger.info(f"⏳ 待發布貼文 ({len(pending_posts)} 篇):")
                for post in pending_posts:
                    logger.info(f"   第{post['row']}行: {post['kol_nickname']} - {post['stock_name']} - {post['title'][:50]}...")
            else:
                logger.info("✅ 沒有待發布的貼文")
            
            # 顯示已發布貼文
            published_posts = []
            for i, row in enumerate(posts_data[1:], 1):
                if len(row) >= 12 and row[11] == 'published':
                    published_posts.append({
                        'row': i + 1,
                        'post_id': row[0],
                        'kol_nickname': row[2] if len(row) > 2 else '',
                        'stock_name': row[3] if len(row) > 3 else '',
                        'title': row[8] if len(row) > 8 else '',
                        'article_id': row[15] if len(row) > 15 else '',
                        'article_url': row[16] if len(row) > 16 else ''
                    })
            
            if published_posts:
                logger.info(f"✅ 已發布貼文 ({len(published_posts)} 篇):")
                for post in published_posts:
                    logger.info(f"   第{post['row']}行: {post['kol_nickname']} - {post['stock_name']} - ID:{post['article_id']}")
            
        except Exception as e:
            logger.error(f"檢查貼文狀態失敗: {e}")

async def main():
    """主函數"""
    checker = PostStatusChecker()
    await checker.check_post_status()

if __name__ == "__main__":
    asyncio.run(main())








