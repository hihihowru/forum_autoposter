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

        # 讀取配置
        logger.info("⚙️  讀取 reaction_bot_config 配置...")
        conn = db_pool.getconn()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM reaction_bot_config WHERE id = 1;")
                config_row = cursor.fetchone()

                if not config_row:
                    logger.error("❌ 找不到配置記錄 (id=1)")
                    return

                # Parse config
                config = {
                    'enabled': config_row[1],
                    'reaction_percentage': config_row[2],
                    'selected_kol_serials': config_row[3] or [],
                    'distribution_algorithm': config_row[4],
                    'min_delay_seconds': config_row[5],
                    'max_delay_seconds': config_row[6],
                    'max_reactions_per_kol_per_hour': config_row[7],
                    'fetch_articles_enabled': config_row[10] if len(config_row) > 10 else True
                }

                logger.info(f"📋 配置: enabled={config['enabled']}, percentage={config['reaction_percentage']}%, KOLs={config['selected_kol_serials'] or 'all'}")

                # Check if enabled
                if not config['enabled']:
                    logger.warning("⏸️  機器人已停用 (enabled=False)，跳過此次任務")
                    return
        finally:
            db_pool.putconn(conn)

        # 計算本小時的時間範圍
        now = datetime.now()
        hour_start = now.replace(minute=0, second=0, microsecond=0)
        hour_end = hour_start + timedelta(hours=1)

        logger.info(f"⏰ 處理時間範圍: {hour_start.strftime('%Y-%m-%d %H:%M')} - {hour_end.strftime('%Y-%m-%d %H:%M')}")

        # 1. 抓取過去 1 小時的文章 (如果啟用)
        if config['fetch_articles_enabled']:
            logger.info("📥 開始抓取過去 1 小時的文章...")
            article_ids = fetch_past_hour_articles(hours=1)
            logger.info(f"✅ 找到 {len(article_ids)} 篇新文章")
        else:
            logger.warning("⏸️  文章抓取已停用 (fetch_articles_enabled=False)，跳過")
            return

        # Apply reaction_percentage filter
        if config['reaction_percentage'] < 100:
            import random
            original_count = len(article_ids)
            keep_count = int(original_count * config['reaction_percentage'] / 100)
            article_ids = random.sample(article_ids, keep_count)
            logger.info(f"🎲 根據 {config['reaction_percentage']}% 比例，從 {original_count} 篇中選擇 {len(article_ids)} 篇")

        # 2. 執行按讚任務（傳入已抓取的 article_ids 和配置）
        logger.info(f"❤️  開始執行按讚任務 (delay: {config['min_delay_seconds']}-{config['max_delay_seconds']}s)...")
        stats = await service.run_hourly_task(
            article_ids=article_ids,
            kol_serials=config['selected_kol_serials'] if config['selected_kol_serials'] else None
        )

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
