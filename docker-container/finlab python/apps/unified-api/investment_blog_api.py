"""
Investment Blog Service - 投資網誌文章抓取服務 (Unified API Version)

Fetches articles from CMoney's investment blog API (newsyoudeservetoknow author)
and tracks sync state to avoid duplicate processing.
"""

import httpx
import logging
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import pytz

logger = logging.getLogger(__name__)


def get_taiwan_now():
    """Get current time in Taiwan timezone"""
    return datetime.now(pytz.timezone('Asia/Taipei'))


def get_db_connection():
    """Get database connection using DATABASE_URL"""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise Exception("DATABASE_URL not set")

    # Railway uses postgres:// but psycopg2 needs postgresql://
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    return psycopg2.connect(database_url)


class InvestmentBlogService:
    """Service for fetching and managing investment blog articles"""

    # CMoney Investment Blog API
    API_BASE_URL = "https://webteam-gateway.cmoney.tw/InvestmentNote/api"
    DEFAULT_AUTHOR_ID = "newsyoudeservetoknow"
    DEFAULT_FETCH_SIZE = 10
    MAX_PAGES = 20  # Safety limit to prevent infinite loops

    def __init__(self):
        self.http_client = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client"""
        if self.http_client is None:
            self.http_client = httpx.AsyncClient(timeout=30.0)
        return self.http_client

    async def close(self):
        """Close HTTP client"""
        if self.http_client:
            await self.http_client.aclose()
            self.http_client = None

    # ==================== Sync State Management ====================

    def get_sync_state(self, author_id: str = None) -> Optional[Dict]:
        """Get sync state for an author"""
        author_id = author_id or self.DEFAULT_AUTHOR_ID
        try:
            conn = get_db_connection()
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT * FROM investment_blog_sync_state
                    WHERE author_id = %s
                """, (author_id,))
                result = cur.fetchone()
            conn.close()
            return dict(result) if result else None
        except Exception as e:
            logger.error(f"Failed to get sync state: {e}")
            return None

    def update_sync_state(
        self,
        author_id: str,
        last_seen_article_id: str,
        articles_count: int = 0
    ) -> bool:
        """Update or create sync state"""
        try:
            conn = get_db_connection()
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO investment_blog_sync_state
                    (author_id, last_seen_article_id, last_sync_at, articles_synced_count)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (author_id)
                    DO UPDATE SET
                        last_seen_article_id = EXCLUDED.last_seen_article_id,
                        last_sync_at = EXCLUDED.last_sync_at,
                        articles_synced_count = investment_blog_sync_state.articles_synced_count + EXCLUDED.articles_synced_count,
                        updated_at = CURRENT_TIMESTAMP
                """, (author_id, last_seen_article_id, get_taiwan_now(), articles_count))
                conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Failed to update sync state: {e}")
            return False

    # ==================== Article Fetching ====================

    async def fetch_article_list(
        self,
        author_id: str = None,
        start_cursor: str = "",
        fetch_size: int = None
    ) -> Tuple[List[Dict], Optional[str], bool]:
        """
        Fetch article list from CMoney API

        Returns:
            Tuple of (articles, next_cursor, has_next_page)
        """
        author_id = author_id or self.DEFAULT_AUTHOR_ID
        fetch_size = fetch_size or self.DEFAULT_FETCH_SIZE

        client = await self._get_client()
        url = f"{self.API_BASE_URL}/Article/{author_id}"
        params = {
            "orderType": "updatedAt",
            "fetch": fetch_size,
        }
        if start_cursor:
            params["startCursor"] = start_cursor

        logger.info(f"📰 Fetching articles: {url} with params {params}")

        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            articles = data.get("authorSummaryArticles", [])
            page_info = data.get("pageInfo", {})
            has_next_page = page_info.get("hasNextPage", False)
            end_cursor = page_info.get("endCursor", "")

            logger.info(f"✅ Fetched {len(articles)} articles, hasNextPage={has_next_page}")
            return articles, end_cursor, has_next_page

        except httpx.HTTPError as e:
            logger.error(f"❌ Failed to fetch article list: {e}")
            raise

    async def fetch_article_content(
        self,
        article_id: str,
        author_id: str = None
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch full article content from CMoney API

        Returns:
            Article with title, content, writer info
        """
        author_id = author_id or self.DEFAULT_AUTHOR_ID
        client = await self._get_client()
        url = f"{self.API_BASE_URL}/Article/{article_id}/Author/{author_id}"

        logger.info(f"📄 Fetching article content: {article_id}")

        try:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()

            article_data = data.get("article", {})
            writer_data = data.get("writer", {})

            return {
                "id": article_id,
                "title": article_data.get("title", ""),
                "content": article_data.get("content", ""),
                "stock_tags": article_data.get("stockTags", []),
                "tags": article_data.get("tags", []),
                "preview_img_url": article_data.get("previewImgUrl", ""),
                "total_views": article_data.get("totalViews", 0),
                "created_at": article_data.get("createAt", 0),
                "updated_at": article_data.get("updateAt", 0),
                "author_id": article_data.get("authorId", author_id),
                "writer_name": writer_data.get("name", "Unknown"),
            }

        except httpx.HTTPError as e:
            logger.error(f"❌ Failed to fetch article content {article_id}: {e}")
            return None

    # ==================== Main Sync Logic ====================

    async def fetch_new_articles(
        self,
        author_id: str = None,
        fetch_content: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Fetch all new articles since last sync.
        """
        author_id = author_id or self.DEFAULT_AUTHOR_ID

        # Get current sync state
        sync_state = self.get_sync_state(author_id)
        last_seen_id = sync_state.get("last_seen_article_id") if sync_state else None

        logger.info(f"🔄 Starting sync for {author_id}, last_seen={last_seen_id}")

        new_articles = []
        first_article_id = None
        cursor = ""
        page = 0
        found_last_seen = False

        try:
            while page < self.MAX_PAGES and not found_last_seen:
                articles, next_cursor, has_next_page = await self.fetch_article_list(
                    author_id=author_id,
                    start_cursor=cursor
                )

                if not articles:
                    break

                # Track first article ID (will become new last_seen)
                if page == 0 and articles:
                    first_article_id = articles[0].get("id")

                for article in articles:
                    article_id = article.get("id")

                    # Stop if we hit the last seen article
                    if article_id == last_seen_id:
                        logger.info(f"🎯 Found last_seen article: {article_id}")
                        found_last_seen = True
                        break

                    # This is a new article
                    article_data = {
                        "id": article_id,
                        "title": article.get("title", ""),
                        "stock_tags": article.get("stockTags", []),
                        "tags": article.get("tags", []),
                        "preview_img_url": article.get("previewImgUrl", ""),
                        "total_views": article.get("totalViews", 0),
                        "updated_at": article.get("updatedAt", 0),
                        "created_at": article.get("createdAt", 0),
                        "author_id": article.get("authorId", author_id),
                    }

                    # Optionally fetch full content
                    if fetch_content:
                        full_content = await self.fetch_article_content(article_id, author_id)
                        if full_content:
                            article_data["content"] = full_content.get("content", "")
                            article_data["writer_name"] = full_content.get("writer_name", "")

                    new_articles.append(article_data)

                # Continue to next page if needed
                if not has_next_page or not next_cursor:
                    break

                cursor = next_cursor
                page += 1

            # Update sync state with first article ID
            if first_article_id:
                self.update_sync_state(
                    author_id=author_id,
                    last_seen_article_id=first_article_id,
                    articles_count=len(new_articles)
                )
                logger.info(f"✅ Updated sync state: last_seen={first_article_id}")

            logger.info(f"✅ Sync complete: {len(new_articles)} new articles found")
            return new_articles

        except Exception as e:
            logger.error(f"❌ Sync failed: {e}")
            raise

    # ==================== Database Operations ====================

    def save_articles(self, articles: List[Dict[str, Any]]) -> int:
        """Save articles to database"""
        saved_count = 0
        try:
            conn = get_db_connection()
            with conn.cursor() as cur:
                for article in articles:
                    try:
                        cur.execute("""
                            INSERT INTO investment_blog_articles
                            (id, author_id, title, content, stock_tags, preview_img_url,
                             total_views, cmoney_updated_at, cmoney_created_at, status)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (id) DO UPDATE SET
                                title = EXCLUDED.title,
                                content = EXCLUDED.content,
                                stock_tags = EXCLUDED.stock_tags,
                                total_views = EXCLUDED.total_views,
                                cmoney_updated_at = EXCLUDED.cmoney_updated_at,
                                updated_at = CURRENT_TIMESTAMP
                        """, (
                            article["id"],
                            article.get("author_id", self.DEFAULT_AUTHOR_ID),
                            article.get("title", ""),
                            article.get("content"),
                            psycopg2.extras.Json(article.get("stock_tags")),
                            article.get("preview_img_url"),
                            article.get("total_views", 0),
                            article.get("updated_at"),
                            article.get("created_at"),
                            "pending"
                        ))
                        saved_count += 1
                    except Exception as e:
                        logger.error(f"Failed to save article {article.get('id')}: {e}")

                conn.commit()
            conn.close()
            logger.info(f"✅ Saved {saved_count} articles to database")
            return saved_count

        except Exception as e:
            logger.error(f"❌ Failed to save articles: {e}")
            raise

    def get_all_articles(self, limit: int = 100, status: str = None) -> List[Dict]:
        """Get all articles with optional status filter"""
        try:
            conn = get_db_connection()
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                if status:
                    cur.execute("""
                        SELECT * FROM investment_blog_articles
                        WHERE status = %s
                        ORDER BY cmoney_created_at DESC NULLS LAST
                        LIMIT %s
                    """, (status, limit))
                else:
                    cur.execute("""
                        SELECT * FROM investment_blog_articles
                        ORDER BY cmoney_created_at DESC NULLS LAST
                        LIMIT %s
                    """, (limit,))
                results = cur.fetchall()
            conn.close()
            return [dict(r) for r in results]
        except Exception as e:
            logger.error(f"Failed to get articles: {e}")
            return []

    def get_article_by_id(self, article_id: str) -> Optional[Dict]:
        """Get single article by ID"""
        try:
            conn = get_db_connection()
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT * FROM investment_blog_articles WHERE id = %s
                """, (article_id,))
                result = cur.fetchone()
            conn.close()
            return dict(result) if result else None
        except Exception as e:
            logger.error(f"Failed to get article: {e}")
            return None

    def update_article_status(
        self,
        article_id: str,
        status: str,
        posted_by: str = None,
        cmoney_post_id: str = None,
        cmoney_post_url: str = None,
        error: str = None
    ) -> bool:
        """Update article posting status"""
        try:
            conn = get_db_connection()
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE investment_blog_articles SET
                        status = %s,
                        posted_by = COALESCE(%s, posted_by),
                        cmoney_post_id = COALESCE(%s, cmoney_post_id),
                        cmoney_post_url = COALESCE(%s, cmoney_post_url),
                        post_error = COALESCE(%s, post_error),
                        posted_at = CASE WHEN %s = 'posted' THEN CURRENT_TIMESTAMP ELSE posted_at END,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, (status, posted_by, cmoney_post_id, cmoney_post_url, error, status, article_id))
                conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Failed to update article status: {e}")
            return False

    # ==================== Auto-Post Management ====================

    def get_auto_post_status(self, author_id: str = None) -> bool:
        """Get auto-post enabled status"""
        author_id = author_id or self.DEFAULT_AUTHOR_ID
        try:
            conn = get_db_connection()
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT auto_post_enabled FROM investment_blog_sync_state
                    WHERE author_id = %s
                """, (author_id,))
                result = cur.fetchone()
            conn.close()
            return result.get("auto_post_enabled", False) if result else False
        except Exception as e:
            logger.error(f"Failed to get auto-post status: {e}")
            return False

    def set_auto_post_status(self, enabled: bool, author_id: str = None) -> bool:
        """Set auto-post enabled status"""
        author_id = author_id or self.DEFAULT_AUTHOR_ID
        try:
            conn = get_db_connection()
            with conn.cursor() as cur:
                # Upsert the status
                cur.execute("""
                    INSERT INTO investment_blog_sync_state (author_id, auto_post_enabled)
                    VALUES (%s, %s)
                    ON CONFLICT (author_id)
                    DO UPDATE SET auto_post_enabled = EXCLUDED.auto_post_enabled,
                                  updated_at = CURRENT_TIMESTAMP
                """, (author_id, enabled))
                conn.commit()
            conn.close()
            logger.info(f"Auto-post {'enabled' if enabled else 'disabled'} for {author_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to set auto-post status: {e}")
            return False

    def get_pending_articles(self, limit: int = 10) -> List[Dict]:
        """Get pending articles for auto-posting"""
        return self.get_all_articles(limit=limit, status="pending")


# Singleton instance
investment_blog_service = InvestmentBlogService()
