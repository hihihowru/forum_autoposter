"""
Investment Blog Service - 投資網誌文章抓取服務

Fetches articles from CMoney's investment blog API (newsyoudeservetoknow author)
and tracks sync state to avoid duplicate processing.
"""

import httpx
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session

from database import get_session_local, InvestmentBlogSyncState, InvestmentBlogArticle
from timezone_utils import get_taiwan_utcnow

logger = logging.getLogger(__name__)


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

    def get_sync_state(self, author_id: str = None) -> Optional[InvestmentBlogSyncState]:
        """Get sync state for an author"""
        author_id = author_id or self.DEFAULT_AUTHOR_ID
        db = get_session_local()()
        try:
            return db.query(InvestmentBlogSyncState).filter(
                InvestmentBlogSyncState.author_id == author_id
            ).first()
        finally:
            db.close()

    def update_sync_state(
        self,
        author_id: str,
        last_seen_article_id: str,
        articles_count: int = 0
    ) -> InvestmentBlogSyncState:
        """Update or create sync state"""
        db = get_session_local()()
        try:
            state = db.query(InvestmentBlogSyncState).filter(
                InvestmentBlogSyncState.author_id == author_id
            ).first()

            if state:
                state.last_seen_article_id = last_seen_article_id
                state.last_sync_at = get_taiwan_utcnow()
                state.articles_synced_count += articles_count
            else:
                state = InvestmentBlogSyncState(
                    author_id=author_id,
                    last_seen_article_id=last_seen_article_id,
                    last_sync_at=get_taiwan_utcnow(),
                    articles_synced_count=articles_count
                )
                db.add(state)

            db.commit()
            db.refresh(state)
            return state
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to update sync state: {e}")
            raise
        finally:
            db.close()

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

        Logic:
        1. Get last_seen_article_id from sync state
        2. Fetch pages until we hit that article ID or reach max pages
        3. For each new article, optionally fetch full content
        4. Update sync state with new first article ID
        5. Return list of new articles

        Args:
            author_id: Author ID to fetch from
            fetch_content: Whether to fetch full content for each article

        Returns:
            List of new articles with content
        """
        author_id = author_id or self.DEFAULT_AUTHOR_ID

        # Get current sync state
        sync_state = self.get_sync_state(author_id)
        last_seen_id = sync_state.last_seen_article_id if sync_state else None

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
        """
        Save articles to database

        Returns:
            Number of articles saved
        """
        db = get_session_local()()
        saved_count = 0

        try:
            for article in articles:
                # Check if article already exists
                existing = db.query(InvestmentBlogArticle).filter(
                    InvestmentBlogArticle.id == article["id"]
                ).first()

                if existing:
                    # Update existing
                    existing.title = article.get("title", existing.title)
                    existing.content = article.get("content", existing.content)
                    existing.stock_tags = article.get("stock_tags", existing.stock_tags)
                    existing.total_views = article.get("total_views", existing.total_views)
                    existing.cmoney_updated_at = article.get("updated_at", existing.cmoney_updated_at)
                else:
                    # Create new
                    db_article = InvestmentBlogArticle(
                        id=article["id"],
                        author_id=article.get("author_id", self.DEFAULT_AUTHOR_ID),
                        title=article.get("title", ""),
                        content=article.get("content"),
                        stock_tags=article.get("stock_tags"),
                        preview_img_url=article.get("preview_img_url"),
                        total_views=article.get("total_views", 0),
                        cmoney_updated_at=article.get("updated_at"),
                        cmoney_created_at=article.get("created_at"),
                        status="pending"
                    )
                    db.add(db_article)
                    saved_count += 1

            db.commit()
            logger.info(f"✅ Saved {saved_count} new articles to database")
            return saved_count

        except Exception as e:
            db.rollback()
            logger.error(f"❌ Failed to save articles: {e}")
            raise
        finally:
            db.close()

    def get_pending_articles(self, limit: int = 50) -> List[InvestmentBlogArticle]:
        """Get articles pending to be posted"""
        db = get_session_local()()
        try:
            return db.query(InvestmentBlogArticle).filter(
                InvestmentBlogArticle.status == "pending"
            ).order_by(
                InvestmentBlogArticle.cmoney_created_at.desc()
            ).limit(limit).all()
        finally:
            db.close()

    def get_all_articles(self, limit: int = 100, status: str = None) -> List[InvestmentBlogArticle]:
        """Get all articles with optional status filter"""
        db = get_session_local()()
        try:
            query = db.query(InvestmentBlogArticle)
            if status:
                query = query.filter(InvestmentBlogArticle.status == status)
            return query.order_by(
                InvestmentBlogArticle.cmoney_created_at.desc()
            ).limit(limit).all()
        finally:
            db.close()

    def update_article_status(
        self,
        article_id: str,
        status: str,
        posted_by: str = None,
        cmoney_post_id: str = None,
        cmoney_post_url: str = None,
        error: str = None
    ) -> Optional[InvestmentBlogArticle]:
        """Update article posting status"""
        db = get_session_local()()
        try:
            article = db.query(InvestmentBlogArticle).filter(
                InvestmentBlogArticle.id == article_id
            ).first()

            if not article:
                return None

            article.status = status
            if posted_by:
                article.posted_by = posted_by
            if cmoney_post_id:
                article.cmoney_post_id = cmoney_post_id
            if cmoney_post_url:
                article.cmoney_post_url = cmoney_post_url
            if error:
                article.post_error = error
            if status == "posted":
                article.posted_at = get_taiwan_utcnow()

            db.commit()
            db.refresh(article)
            return article

        except Exception as e:
            db.rollback()
            logger.error(f"❌ Failed to update article status: {e}")
            raise
        finally:
            db.close()


# Singleton instance
investment_blog_service = InvestmentBlogService()
