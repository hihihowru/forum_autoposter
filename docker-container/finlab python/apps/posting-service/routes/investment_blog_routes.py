"""
Investment Blog API Routes - 投資網誌 API 路由

Endpoints for fetching and posting investment blog articles.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/investment-blog", tags=["investment-blog"])


# ==================== Request/Response Models ====================

class FetchArticlesRequest(BaseModel):
    author_id: Optional[str] = "newsyoudeservetoknow"
    fetch_content: Optional[bool] = True


class FetchArticlesResponse(BaseModel):
    success: bool
    message: str
    articles_count: int
    new_articles_count: int
    articles: List[Dict[str, Any]]


class PostArticleRequest(BaseModel):
    article_id: str
    poster_email: str = "forum_190@cmoney.com.tw"
    stock_tags: Optional[List[str]] = None  # Override stock tags if needed


class PostArticleResponse(BaseModel):
    success: bool
    message: str
    article_id: str
    cmoney_post_id: Optional[str] = None
    cmoney_post_url: Optional[str] = None


class SyncStateResponse(BaseModel):
    author_id: str
    last_seen_article_id: Optional[str]
    last_sync_at: Optional[str]
    articles_synced_count: int


class ArticleListResponse(BaseModel):
    success: bool
    articles: List[Dict[str, Any]]
    total: int


# ==================== Lazy Service Import ====================

_investment_blog_service = None
_publish_service = None


def get_investment_blog_service():
    global _investment_blog_service
    if _investment_blog_service is None:
        from investment_blog_service import investment_blog_service
        _investment_blog_service = investment_blog_service
    return _investment_blog_service


def get_publish_service():
    global _publish_service
    if _publish_service is None:
        try:
            from publish_service import publish_service
            _publish_service = publish_service
        except Exception as e:
            logger.error(f"Failed to import publish_service: {e}")
            return None
    return _publish_service


# ==================== API Endpoints ====================

@router.get("/sync-state")
async def get_sync_state(author_id: str = "newsyoudeservetoknow") -> SyncStateResponse:
    """
    Get current sync state for an author.
    Shows last synced article ID and sync timestamp.
    """
    try:
        service = get_investment_blog_service()
        state = service.get_sync_state(author_id)

        if state:
            return SyncStateResponse(
                author_id=state.author_id,
                last_seen_article_id=state.last_seen_article_id,
                last_sync_at=state.last_sync_at.isoformat() if state.last_sync_at else None,
                articles_synced_count=state.articles_synced_count
            )
        else:
            return SyncStateResponse(
                author_id=author_id,
                last_seen_article_id=None,
                last_sync_at=None,
                articles_synced_count=0
            )

    except Exception as e:
        logger.error(f"Failed to get sync state: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/fetch")
async def fetch_new_articles(request: FetchArticlesRequest) -> FetchArticlesResponse:
    """
    Fetch new articles from CMoney API.

    This will:
    1. Get last_seen_article_id from database
    2. Fetch pages until hitting that article or reaching end
    3. Save new articles to database
    4. Update sync state with new first article ID
    5. Return list of new articles
    """
    try:
        service = get_investment_blog_service()

        # Fetch new articles
        new_articles = await service.fetch_new_articles(
            author_id=request.author_id,
            fetch_content=request.fetch_content
        )

        # Save to database
        saved_count = 0
        if new_articles:
            saved_count = service.save_articles(new_articles)

        # Convert articles for response
        articles_data = []
        for article in new_articles:
            articles_data.append({
                "id": article.get("id"),
                "title": article.get("title"),
                "content": article.get("content", "")[:500] + "..." if article.get("content") and len(article.get("content", "")) > 500 else article.get("content", ""),
                "stock_tags": article.get("stock_tags", []),
                "preview_img_url": article.get("preview_img_url"),
                "total_views": article.get("total_views", 0),
                "created_at": article.get("created_at"),
                "updated_at": article.get("updated_at"),
                "status": "pending"
            })

        return FetchArticlesResponse(
            success=True,
            message=f"Fetched {len(new_articles)} new articles, saved {saved_count} to database",
            articles_count=len(new_articles),
            new_articles_count=saved_count,
            articles=articles_data
        )

    except Exception as e:
        logger.error(f"Failed to fetch articles: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/articles")
async def get_articles(
    status: Optional[str] = None,
    limit: int = 50
) -> ArticleListResponse:
    """
    Get articles from database.

    Args:
        status: Filter by status (pending, posted, skipped, failed)
        limit: Max number of articles to return
    """
    try:
        service = get_investment_blog_service()
        articles = service.get_all_articles(limit=limit, status=status)

        articles_data = []
        for article in articles:
            articles_data.append({
                "id": article.id,
                "title": article.title,
                "content": article.content[:500] + "..." if article.content and len(article.content) > 500 else article.content,
                "stock_tags": article.stock_tags or [],
                "preview_img_url": article.preview_img_url,
                "total_views": article.total_views,
                "status": article.status,
                "posted_at": article.posted_at.isoformat() if article.posted_at else None,
                "posted_by": article.posted_by,
                "cmoney_post_url": article.cmoney_post_url,
                "fetched_at": article.fetched_at.isoformat() if article.fetched_at else None,
                "cmoney_created_at": article.cmoney_created_at,
                "cmoney_updated_at": article.cmoney_updated_at,
            })

        return ArticleListResponse(
            success=True,
            articles=articles_data,
            total=len(articles_data)
        )

    except Exception as e:
        logger.error(f"Failed to get articles: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/articles/{article_id}")
async def get_article(article_id: str) -> Dict[str, Any]:
    """Get single article with full content"""
    try:
        service = get_investment_blog_service()
        from database import get_session_local, InvestmentBlogArticle

        db = get_session_local()()
        try:
            article = db.query(InvestmentBlogArticle).filter(
                InvestmentBlogArticle.id == article_id
            ).first()

            if not article:
                raise HTTPException(status_code=404, detail="Article not found")

            return {
                "success": True,
                "article": {
                    "id": article.id,
                    "title": article.title,
                    "content": article.content,  # Full content
                    "stock_tags": article.stock_tags or [],
                    "preview_img_url": article.preview_img_url,
                    "total_views": article.total_views,
                    "status": article.status,
                    "posted_at": article.posted_at.isoformat() if article.posted_at else None,
                    "posted_by": article.posted_by,
                    "cmoney_post_id": article.cmoney_post_id,
                    "cmoney_post_url": article.cmoney_post_url,
                    "post_error": article.post_error,
                    "fetched_at": article.fetched_at.isoformat() if article.fetched_at else None,
                    "cmoney_created_at": article.cmoney_created_at,
                    "cmoney_updated_at": article.cmoney_updated_at,
                }
            }
        finally:
            db.close()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get article: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/post")
async def post_article(request: PostArticleRequest) -> PostArticleResponse:
    """
    Post an article to CMoney forum.

    This will:
    1. Get article from database
    2. Login with designated poster account
    3. Create forum post with stock tags
    4. Update article status in database
    """
    try:
        service = get_investment_blog_service()

        # Get article from database
        from database import get_session_local, InvestmentBlogArticle
        db = get_session_local()()

        try:
            article = db.query(InvestmentBlogArticle).filter(
                InvestmentBlogArticle.id == request.article_id
            ).first()

            if not article:
                raise HTTPException(status_code=404, detail="Article not found")

            if article.status == "posted":
                return PostArticleResponse(
                    success=False,
                    message="Article already posted",
                    article_id=request.article_id,
                    cmoney_post_url=article.cmoney_post_url
                )

            # Use stock tags from request or article
            stock_tags = request.stock_tags or article.stock_tags or []

            # Format commodity tags for CMoney
            commodity_tags = []
            for stock_code in stock_tags:
                commodity_tags.append({
                    "type": "Stock",
                    "key": stock_code,
                    "bullOrBear": 0  # Neutral
                })

            logger.info(f"📤 Publishing article {article.id} with {len(commodity_tags)} stock tags")

            # Import CMoney client and publish directly
            import sys
            src_path = '/app/src'
            if src_path not in sys.path:
                sys.path.insert(0, src_path)

            from src.clients.cmoney.cmoney_client import CMoneyClient, LoginCredentials, ArticleData

            # Get poster credentials - forum_190
            poster_email = request.poster_email
            poster_password = get_poster_password(poster_email)

            if not poster_password:
                raise HTTPException(status_code=400, detail=f"No credentials found for {poster_email}")

            # Login
            cmoney_client = CMoneyClient()
            credentials = LoginCredentials(email=poster_email, password=poster_password)
            access_token = await cmoney_client.login(credentials)

            if not access_token or not access_token.token:
                raise HTTPException(status_code=401, detail="Login failed")

            logger.info(f"✅ Logged in as {poster_email}")

            # Build article data
            article_data = ArticleData(
                title=article.title,
                text=article.content,
                commodity_tags=commodity_tags if commodity_tags else None,
                communityTopic=None
            )

            # Publish
            publish_result = await cmoney_client.publish_article(access_token.token, article_data)

            if publish_result.success:
                post_url = f"https://www.cmoney.tw/forum/article/{publish_result.post_id}"

                # Update article status
                service.update_article_status(
                    article_id=article.id,
                    status="posted",
                    posted_by=poster_email,
                    cmoney_post_id=publish_result.post_id,
                    cmoney_post_url=post_url
                )

                logger.info(f"✅ Article posted: {post_url}")

                return PostArticleResponse(
                    success=True,
                    message="Article posted successfully",
                    article_id=request.article_id,
                    cmoney_post_id=publish_result.post_id,
                    cmoney_post_url=post_url
                )
            else:
                # Update with error
                service.update_article_status(
                    article_id=article.id,
                    status="failed",
                    error=publish_result.error_message or "Unknown error"
                )

                return PostArticleResponse(
                    success=False,
                    message=f"Failed to post: {publish_result.error_message or 'Unknown error'}",
                    article_id=request.article_id
                )

        finally:
            db.close()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to post article: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# Poster credentials lookup
POSTER_CREDENTIALS = {
    "forum_186@cmoney.com.tw": "t7L9uY0f",
    "forum_187@cmoney.com.tw": "a4E9jV8t",
    "forum_188@cmoney.com.tw": "z6G5wN2m",
    "forum_189@cmoney.com.tw": "c8L5nO3q",
    "forum_190@cmoney.com.tw": "W4x6hU0r",
    "forum_191@cmoney.com.tw": "H7u4rE2j",
    "forum_192@cmoney.com.tw": "S3c6oJ9h",
    "forum_193@cmoney.com.tw": "X2t1vU7l",
    "forum_194@cmoney.com.tw": "j3H5dM7p",
    "forum_195@cmoney.com.tw": "P9n1fT3x",
    "forum_196@cmoney.com.tw": "b4C1pL3r",
    "forum_197@cmoney.com.tw": "O8a3pF4c",
    "forum_198@cmoney.com.tw": "i0L5fC3s",
}


def get_poster_password(email: str) -> Optional[str]:
    """Get password for poster email"""
    return POSTER_CREDENTIALS.get(email)


@router.post("/articles/{article_id}/skip")
async def skip_article(article_id: str) -> Dict[str, Any]:
    """Mark an article as skipped (won't be posted)"""
    try:
        service = get_investment_blog_service()
        article = service.update_article_status(article_id, status="skipped")

        if not article:
            raise HTTPException(status_code=404, detail="Article not found")

        return {
            "success": True,
            "message": "Article marked as skipped",
            "article_id": article_id
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to skip article: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/articles/{article_id}/reset")
async def reset_article(article_id: str) -> Dict[str, Any]:
    """Reset an article status back to pending"""
    try:
        service = get_investment_blog_service()
        article = service.update_article_status(article_id, status="pending")

        if not article:
            raise HTTPException(status_code=404, detail="Article not found")

        return {
            "success": True,
            "message": "Article reset to pending",
            "article_id": article_id
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to reset article: {e}")
        raise HTTPException(status_code=500, detail=str(e))
