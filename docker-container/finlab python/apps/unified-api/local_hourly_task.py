#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
本地每小時任務 - 從 CMoney 抓取文章並按讚，存儲到 Railway 數據庫
Local Hourly Task - Fetch articles from CMoney and like them, save to Railway DB

運行方式 / Usage:
    python local_hourly_task.py

設置 cronjob / Setup cronjob:
    crontab -e
    # 每小時運行一次 (Run every hour at minute 0)
    0 * * * * cd "/Users/willchen/Documents/autoposter/forum_autoposter/docker-container/finlab python/apps/unified-api" && /usr/bin/python3 local_hourly_task.py >> /tmp/hourly_task.log 2>&1
"""

import asyncio
import logging
import os
import urllib.parse
from datetime import datetime, timedelta
from psycopg2 import pool

from hourly_reaction_service import HourlyReactionService
from cmoney_reaction_client import CMoneyReactionClient
from cmoney_article_fetcher import fetch_past_hour_articles

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """主函數 - 執行每小時任務"""

    logger.info("=" * 70)
    logger.info("🚀 開始執行本地每小時任務...")
    logger.info("=" * 70)

    # 從環境變數讀取 Railway 數據庫 URL
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        # 如果沒有設置，使用 Railway 的公開 PostgreSQL URL
        logger.error("❌ DATABASE_URL 環境變數未設置")
        logger.info("💡 請設置環境變數:")
        logger.info("   export DATABASE_URL='postgresql://postgres:PASSWORD@HOST:PORT/railway'")
        return

    parsed_url = urllib.parse.urlparse(database_url)

    # 建立資料庫連線池
    logger.info(f"🔗 連接到 Railway 數據庫: {parsed_url.hostname}")
    db_pool = pool.SimpleConnectionPool(
        minconn=1,
        maxconn=5,
        host=parsed_url.hostname,
        port=parsed_url.port or 5432,
        database=parsed_url.path[1:],
        user=parsed_url.username,
        password=parsed_url.password
    )

    try:
        # 初始化服務
        cmoney_client = CMoneyReactionClient()
        service = HourlyReactionService(db_pool, cmoney_client)

        # 確保資料表存在
        logger.info("📊 確保 hourly_reaction_stats 資料表存在...")
        service.create_hourly_stats_table()

        # 計算本小時的時間範圍
        now = datetime.now()
        hour_start = now.replace(minute=0, second=0, microsecond=0)
        hour_end = hour_start + timedelta(hours=1)

        logger.info(f"⏰ 處理時間範圍: {hour_start.strftime('%Y-%m-%d %H:%M')} - {hour_end.strftime('%Y-%m-%d %H:%M')}")

        # 1. 抓取過去 1 小時的文章
        logger.info("📥 開始抓取過去 1 小時的文章...")
        article_ids = fetch_past_hour_articles(hours=1)

        if not article_ids:
            logger.warning("⚠️  沒有找到新文章")
            # 儲存空統計
            service.save_hourly_stats(
                hour_start=hour_start,
                total_articles=0,
                total_attempts=0,
                successful_likes=0,
                unique_articles=0,
                kol_serials=[],
                article_ids=[]
            )
            logger.info("✅ 已儲存空統計記錄")
            return

        logger.info(f"✅ 找到 {len(article_ids)} 篇新文章")

        # 2. 執行按讚任務
        logger.info("❤️  開始執行按讚任務...")
        stats = await service.run_hourly_task()

        # 3. 顯示結果
        logger.info("=" * 70)
        logger.info("📊 執行結果:")
        logger.info(f"   時間範圍: {stats['hour_start']} - {stats['hour_end']}")
        logger.info(f"   總文章數: {stats['total_new_articles']}")
        logger.info(f"   按讚嘗試: {stats['total_like_attempts']}")
        logger.info(f"   成功按讚: {stats['successful_likes']}")
        logger.info(f"   成功率: {stats['like_success_rate']:.2f}%")
        logger.info(f"   使用 KOL: {stats['kol_pool_serials']}")
        logger.info("=" * 70)
        logger.info("✅ 本地每小時任務執行完成!")

    except Exception as e:
        logger.error(f"❌ 執行失敗: {e}", exc_info=True)
        raise

    finally:
        # 清理資源
        db_pool.closeall()
        logger.info("🧹 資源清理完成")


if __name__ == "__main__":
    asyncio.run(main())
