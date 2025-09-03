#!/usr/bin/env python3
"""
創建「aigc 自我學習機制」分頁並設置標題行
"""

import asyncio
import logging
from src.clients.google.sheets_client import GoogleSheetsClient

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def create_learning_mechanism_sheet():
    """創建「aigc 自我學習機制」分頁"""
    try:
        sheets_client = GoogleSheetsClient(
            credentials_file='credentials/google-service-account.json',
            spreadsheet_id='148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LikN2s'
        )
        
        # 標題行
        headers = [
            'article_id',
            'member_id', 
            'nickname',
            'title',
            'content',
            'topic_id',
            'is_trending_topic',
            'post_time',
            'last_update_time',
            'likes_count',
            'comments_count',
            'total_interactions',
            'engagement_rate',
            'growth_rate',
            'collection_error'
        ]
        
        # 嘗試寫入標題行到「aigc 自我學習機制」分頁
        try:
            sheets_client.write_sheet('aigc 自我學習機制', [headers], 'A1:O1')
            logger.info("✅ 成功創建「aigc 自我學習機制」分頁並設置標題行")
            return True
        except Exception as e:
            logger.error(f"❌ 無法創建「aigc 自我學習機制」分頁: {e}")
            
            # 嘗試其他可能的名稱
            alternative_names = [
                'aigc自我學習機制',
                '自我學習機制',
                'aigc',
                'learning_mechanism'
            ]
            
            for name in alternative_names:
                try:
                    sheets_client.write_sheet(name, [headers], 'A1:O1')
                    logger.info(f"✅ 成功創建「{name}」分頁並設置標題行")
                    return name
                except:
                    continue
            
            logger.error("❌ 無法創建任何分頁")
            return False
            
    except Exception as e:
        logger.error(f"創建分頁失敗: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(create_learning_mechanism_sheet())
