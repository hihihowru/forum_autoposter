# -*- coding: utf-8 -*-
"""
Hourly Reaction Service
每小時互動服務：抓取新文章、執行按讚、記錄統計
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import psycopg2
from psycopg2.extras import RealDictCursor
from cmoney_article_fetcher import fetch_past_hour_articles
from cmoney_reaction_client import CMoneyReactionClient

logger = logging.getLogger(__name__)


class HourlyReactionService:
    """每小時互動服務"""

    def __init__(self, db_pool, cmoney_client: CMoneyReactionClient):
        self.db_pool = db_pool
        self.cmoney_client = cmoney_client

    def create_hourly_stats_table(self):
        """建立 hourly_reaction_stats 資料表"""
        conn = None
        try:
            conn = self.db_pool.getconn()
            with conn.cursor() as cursor:
                # 讀取 SQL 檔案
                with open('migrations/create_hourly_reaction_stats.sql', 'r', encoding='utf-8') as f:
                    sql = f.read()

                cursor.execute(sql)
                conn.commit()
                logger.info("✅ [Hourly Stats] Table created successfully")

        except Exception as e:
            logger.error(f"❌ [Hourly Stats] Failed to create table: {e}")
            if conn:
                conn.rollback()
            raise

        finally:
            if conn:
                self.db_pool.putconn(conn)

    def get_kol_pool(self, kol_serials: Optional[List[int]] = None) -> List[Dict]:
        """
        取得 KOL 池子

        Args:
            kol_serials: 指定的 KOL serial 列表（None = 全部）

        Returns:
            List of KOL profiles with email, password, serial
        """
        conn = None
        try:
            conn = self.db_pool.getconn()
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                if kol_serials:
                    cursor.execute("""
                        SELECT serial, email, password, nickname
                        FROM kol_profiles
                        WHERE serial = ANY(%s)
                        AND status = 'active'
                        ORDER BY serial
                    """, (kol_serials,))
                else:
                    cursor.execute("""
                        SELECT serial, email, password, nickname
                        FROM kol_profiles
                        WHERE status = 'active'
                        ORDER BY serial
                    """)

                kols = cursor.fetchall()
                logger.info(f"✅ [KOL Pool] Loaded {len(kols)} KOLs")
                return [dict(kol) for kol in kols]

        except Exception as e:
            logger.error(f"❌ [KOL Pool] Failed to load: {e}")
            return []

        finally:
            if conn:
                self.db_pool.putconn(conn)

    async def process_hourly_batch(
        self,
        article_ids: List[int],
        kol_pool: List[Dict],
        articles_per_kol: int = 10
    ) -> Tuple[int, int, int]:
        """
        處理一批文章的按讚

        Args:
            article_ids: 文章 ID 列表
            kol_pool: KOL 池子
            articles_per_kol: 每個 KOL 按讚幾篇文章後切換

        Returns:
            (total_attempts, successful_likes, unique_articles_liked)
        """
        total_attempts = 0
        successful_likes = 0
        liked_articles = set()

        current_kol_index = 0
        current_kol_token = None
        current_kol_article_count = 0

        for article_id in article_ids:
            # 檢查是否需要切換 KOL
            if current_kol_article_count >= articles_per_kol or current_kol_token is None:
                current_kol = kol_pool[current_kol_index % len(kol_pool)]

                # 登入取得 token
                logger.info(f"🔑 [Login] Logging in KOL: {current_kol['nickname']} (serial={current_kol['serial']})")

                token = await self.cmoney_client.get_or_refresh_token(
                    kol_serial=current_kol['serial'],
                    email=current_kol['email'],
                    password=current_kol['password']
                )

                if not token:
                    logger.error(f"❌ [Login] Failed for KOL {current_kol['nickname']}")
                    current_kol_index += 1
                    current_kol_article_count = 0
                    continue

                current_kol_token = token
                current_kol_article_count = 0
                logger.info(f"✅ [Login] Success for KOL {current_kol['nickname']}")

            # 按讚
            total_attempts += 1
            logger.info(f"👍 [Like] Attempting to like article {article_id} with KOL {current_kol['nickname']}")

            import time
            start_time = time.time()

            result = await self.cmoney_client.add_article_reaction(
                access_token=current_kol_token,
                article_id=str(article_id),
                reaction_type=1  # 1 = 讚
            )

            response_time_ms = int((time.time() - start_time) * 1000)

            # Log to database
            self._log_reaction_to_db(
                article_id=str(article_id),
                kol_serial=current_kol['serial'],
                kol_nickname=current_kol['nickname'],
                reaction_type=1,
                success=result.success,
                http_status_code=getattr(result, 'http_status_code', None),
                error_message=result.error_message,
                response_time_ms=response_time_ms
            )

            if result.success:
                successful_likes += 1
                liked_articles.add(article_id)
                logger.info(f"✅ [Like] Success for article {article_id} ({response_time_ms}ms)")
            else:
                logger.warning(f"⚠️  [Like] Failed for article {article_id}: {result.error_message}")

            current_kol_article_count += 1

            # 延遲避免 rate limit
            await asyncio.sleep(2)

        unique_articles_liked = len(liked_articles)
        logger.info(f"📊 [Batch Complete] Attempts={total_attempts}, Success={successful_likes}, Unique={unique_articles_liked}")

        return total_attempts, successful_likes, unique_articles_liked

    def _log_reaction_to_db(
        self,
        article_id: str,
        kol_serial: int,
        kol_nickname: str,
        reaction_type: int,
        success: bool,
        http_status_code: Optional[int],
        error_message: Optional[str],
        response_time_ms: int
    ):
        """記錄單次反應到資料庫"""
        conn = None
        try:
            conn = self.db_pool.getconn()
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO reaction_logs (
                        article_id, kol_serial, kol_nickname, reaction_type,
                        success, http_status_code, error_message, response_time_ms
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    article_id, kol_serial, kol_nickname, reaction_type,
                    success, http_status_code, error_message, response_time_ms
                ))
                conn.commit()

        except Exception as e:
            logger.error(f"❌ [Log Reaction] Failed to log: {e}")
            if conn:
                conn.rollback()

        finally:
            if conn:
                self.db_pool.putconn(conn)

    def save_hourly_stats(
        self,
        hour_start: datetime,
        total_articles: int,
        total_attempts: int,
        successful_likes: int,
        unique_articles: int,
        kol_serials: List[int],
        article_ids: List[int]
    ):
        """儲存小時統計"""
        conn = None
        try:
            conn = self.db_pool.getconn()
            with conn.cursor() as cursor:
                hour_end = hour_start + timedelta(hours=1)
                like_rate = (successful_likes / total_articles * 100) if total_articles > 0 else 0

                cursor.execute("""
                    INSERT INTO hourly_reaction_stats (
                        hour_start, hour_end, total_new_articles,
                        total_like_attempts, successful_likes, unique_articles_liked,
                        like_success_rate, kol_pool_serials, article_ids
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                    ON CONFLICT (hour_start) DO UPDATE SET
                        total_like_attempts = EXCLUDED.total_like_attempts,
                        successful_likes = EXCLUDED.successful_likes,
                        unique_articles_liked = EXCLUDED.unique_articles_liked,
                        like_success_rate = EXCLUDED.like_success_rate,
                        updated_at = CURRENT_TIMESTAMP
                """, (
                    hour_start, hour_end, total_articles,
                    total_attempts, successful_likes, unique_articles,
                    like_rate, kol_serials, [str(aid) for aid in article_ids]
                ))

                conn.commit()
                logger.info(f"✅ [Save Stats] Saved for hour {hour_start}")

                # Auto-cleanup logs older than 2 days
                cursor.execute("""
                    DELETE FROM reaction_logs
                    WHERE attempted_at < NOW() - INTERVAL '2 days'
                """)
                deleted_count = cursor.rowcount
                if deleted_count > 0:
                    logger.info(f"🧹 [Cleanup] Deleted {deleted_count} old reaction logs (>2 days)")
                conn.commit()

        except Exception as e:
            logger.error(f"❌ [Save Stats] Failed: {e}")
            if conn:
                conn.rollback()

        finally:
            if conn:
                self.db_pool.putconn(conn)

    async def run_hourly_task(self, kol_serials: Optional[List[int]] = None, article_ids: Optional[List[int]] = None):
        """
        執行每小時任務

        Args:
            kol_serials: 指定的 KOL serial 列表（None = 全部）
            article_ids: 已抓取的文章 ID 列表（None = 從函數內抓取）

        Returns:
            Dict with stats: hour_start, hour_end, total_new_articles, etc.
        """
        hour_start = datetime.now().replace(minute=0, second=0, microsecond=0)
        hour_end = hour_start + timedelta(hours=1)

        logger.info(f"🚀 [Hourly Task] Starting for hour {hour_start}")

        # 1. 抓取過去一小時文章（如果沒有傳入）
        if article_ids is None:
            article_ids = fetch_past_hour_articles()

        total_articles = len(article_ids)

        logger.info(f"📰 [Hourly Task] Found {total_articles} new articles")

        if total_articles == 0:
            logger.info("⚠️  [Hourly Task] No articles to process")
            return {
                'hour_start': hour_start,
                'hour_end': hour_end,
                'total_new_articles': 0,
                'total_like_attempts': 0,
                'successful_likes': 0,
                'unique_articles_liked': 0,
                'like_success_rate': 0.0,
                'kol_pool_serials': []
            }

        # 2. 取得 KOL 池子
        kol_pool = self.get_kol_pool(kol_serials)

        if not kol_pool:
            logger.error("❌ [Hourly Task] No KOLs available")
            return {
                'hour_start': hour_start,
                'hour_end': hour_end,
                'total_new_articles': total_articles,
                'total_like_attempts': 0,
                'successful_likes': 0,
                'unique_articles_liked': 0,
                'like_success_rate': 0.0,
                'kol_pool_serials': []
            }

        # 3. 執行按讚
        total_attempts, successful_likes, unique_articles = await self.process_hourly_batch(
            article_ids=article_ids,
            kol_pool=kol_pool,
            articles_per_kol=10
        )

        # 4. 儲存統計
        kol_serials_list = [kol['serial'] for kol in kol_pool]
        self.save_hourly_stats(
            hour_start=hour_start,
            total_articles=total_articles,
            total_attempts=total_attempts,
            successful_likes=successful_likes,
            unique_articles=unique_articles,
            kol_serials=kol_serials_list,
            article_ids=article_ids
        )

        logger.info(f"✅ [Hourly Task] Completed for hour {hour_start}")

        # 返回統計結果
        like_rate = (successful_likes / total_articles * 100) if total_articles > 0 else 0
        return {
            'hour_start': hour_start,
            'hour_end': hour_end,
            'total_new_articles': total_articles,
            'total_like_attempts': total_attempts,
            'successful_likes': successful_likes,
            'unique_articles_liked': unique_articles,
            'like_success_rate': like_rate,
            'kol_pool_serials': kol_serials_list
        }


# 測試用
async def test_hourly_service():
    """測試服務"""
    import os
    from psycopg2 import pool

    # 建立資料庫連線池
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        import urllib.parse
        parsed_url = urllib.parse.urlparse(database_url)

        db_pool = pool.SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            host=parsed_url.hostname,
            port=parsed_url.port or 5432,
            database=parsed_url.path[1:],
            user=parsed_url.username,
            password=parsed_url.password
        )

        # 建立服務
        cmoney_client = CMoneyReactionClient()
        service = HourlyReactionService(db_pool, cmoney_client)

        # 建立資料表
        service.create_hourly_stats_table()

        # 執行任務
        await service.run_hourly_task()

        db_pool.closeall()
    else:
        print("DATABASE_URL not set")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_hourly_service())
