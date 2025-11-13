"""
Reaction Bot API Routes
FastAPI routes for reaction bot management

Created: 2025-11-10
Author: Claude Code
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import logging

from reaction_bot_service import ReactionBotService, ReactionBotConfig

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/reaction-bot", tags=["Reaction Bot"])


# ============================================
# Request/Response Models
# ============================================

class ConfigUpdateRequest(BaseModel):
    """Request model for updating config"""
    enabled: Optional[bool] = None
    reaction_percentage: Optional[int] = Field(None, ge=0, le=1000, description="Percentage (100=1x, 200=2x)")
    selected_kol_serials: Optional[List[int]] = None
    distribution_algorithm: Optional[str] = Field(None, pattern="^(poisson|uniform|weighted)$")
    min_delay_seconds: Optional[float] = Field(None, ge=0.1, le=10.0)
    max_delay_seconds: Optional[float] = Field(None, ge=0.1, le=10.0)
    max_reactions_per_kol_per_hour: Optional[int] = Field(None, ge=1, le=1000)


class ProcessBatchRequest(BaseModel):
    """Request model for processing article batch"""
    article_ids: List[str] = Field(..., min_items=1, description="List of article IDs")
    batch_id: Optional[str] = None


class ConfigResponse(BaseModel):
    """Response model for config"""
    enabled: bool
    reaction_percentage: int
    selected_kol_serials: List[int]
    distribution_algorithm: str
    min_delay_seconds: float
    max_delay_seconds: float
    max_reactions_per_kol_per_hour: int
    created_at: str
    updated_at: str


class StatsResponse(BaseModel):
    """Response model for stats"""
    daily_stats: List[Dict[str, Any]]
    overall: Dict[str, Any]
    period_days: int


class BatchProcessResponse(BaseModel):
    """Response model for batch processing"""
    success: bool
    batch_id: str
    reactions_sent: int
    reactions_failed: int
    total_articles: int
    total_reactions: int
    message: Optional[str] = None


# ============================================
# Dependency: Get ReactionBotService
# ============================================

async def get_reaction_bot_service():
    """
    Dependency to get ReactionBotService instance from main app globals.
    """
    from main import reaction_bot_service
    return reaction_bot_service


# ============================================
# API Endpoints
# ============================================

@router.get("/config", response_model=ConfigResponse, summary="Get reaction bot configuration")
async def get_config(service: ReactionBotService = Depends(get_reaction_bot_service)):
    """
    Get current reaction bot configuration.

    Returns:
        Current configuration settings
    """
    try:
        if not service:
            raise HTTPException(status_code=503, detail="Service not available")

        config = await service.get_config()

        if not config:
            raise HTTPException(status_code=404, detail="Configuration not found")

        return config

    except Exception as e:
        logger.error(f"❌ Error getting config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/config", response_model=Dict[str, Any], summary="Update reaction bot configuration")
async def update_config(
    updates: ConfigUpdateRequest,
    service: ReactionBotService = Depends(get_reaction_bot_service)
):
    """
    Update reaction bot configuration.

    Args:
        updates: Configuration updates

    Returns:
        Updated configuration
    """
    try:
        if not service:
            raise HTTPException(status_code=503, detail="Service not available")

        # Convert to dict, excluding None values
        config_updates = updates.dict(exclude_none=True)

        if not config_updates:
            raise HTTPException(status_code=400, detail="No fields to update")

        # Validate min/max delay
        if 'min_delay_seconds' in config_updates and 'max_delay_seconds' in config_updates:
            if config_updates['min_delay_seconds'] > config_updates['max_delay_seconds']:
                raise HTTPException(
                    status_code=400,
                    detail="min_delay_seconds cannot be greater than max_delay_seconds"
                )

        updated_config = await service.update_config(config_updates)

        logger.info(f"✅ Config updated: {config_updates}")

        return {
            "success": True,
            "message": "Configuration updated successfully",
            "config": updated_config
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"❌ Error updating config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/process-batch", response_model=BatchProcessResponse, summary="Process article batch")
async def process_batch(
    request: ProcessBatchRequest,
    service: ReactionBotService = Depends(get_reaction_bot_service)
):
    """
    Process a batch of article IDs and send reactions.

    This endpoint will:
    1. Validate configuration
    2. Calculate total reactions based on percentage
    3. Distribute reactions using Poisson distribution
    4. Send reactions via CMoney API with delays
    5. Log all activity

    Args:
        request: Batch processing request with article IDs

    Returns:
        Processing result summary
    """
    try:
        if not service:
            raise HTTPException(status_code=503, detail="Service not available")

        if service.processing:
            raise HTTPException(status_code=409, detail="Bot is already processing a batch")

        result = await service.process_article_batch(
            article_ids=request.article_ids,
            batch_id=request.batch_id
        )

        return result

    except RuntimeError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"❌ Error processing batch: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", response_model=StatsResponse, summary="Get reaction bot statistics")
async def get_stats(
    days: int = 7,
    service: ReactionBotService = Depends(get_reaction_bot_service)
):
    """
    Get reaction bot statistics for the specified number of days.

    Args:
        days: Number of days to include (default: 7, max: 90)

    Returns:
        Statistics summary including daily breakdown and overall metrics
    """
    try:
        if not service:
            raise HTTPException(status_code=503, detail="Service not available")

        if days < 1 or days > 90:
            raise HTTPException(status_code=400, detail="Days must be between 1 and 90")

        stats = await service.get_stats(days=days)

        return stats

    except Exception as e:
        logger.error(f"❌ Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/logs", summary="Get reaction bot logs")
async def get_logs(
    limit: int = 100,
    offset: int = 0,
    article_id: Optional[str] = None,
    kol_serial: Optional[int] = None,
    success: Optional[bool] = None,
    service: ReactionBotService = Depends(get_reaction_bot_service)
):
    """
    Get reaction bot activity logs with filtering.

    Args:
        limit: Maximum number of logs to return (default: 100, max: 1000)
        offset: Pagination offset (default: 0)
        article_id: Filter by article ID
        kol_serial: Filter by KOL serial
        success: Filter by success status

    Returns:
        List of log entries
    """
    try:
        if not service:
            raise HTTPException(status_code=503, detail="Service not available")

        if limit < 1 or limit > 1000:
            raise HTTPException(status_code=400, detail="Limit must be between 1 and 1000")

        # Build WHERE clause
        where_clauses = []
        params = []
        param_count = 1

        if article_id:
            where_clauses.append(f"article_id = ${param_count}")
            params.append(article_id)
            param_count += 1

        if kol_serial is not None:
            where_clauses.append(f"kol_serial = ${param_count}")
            params.append(kol_serial)
            param_count += 1

        if success is not None:
            where_clauses.append(f"success = ${param_count}")
            params.append(success)
            param_count += 1

        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"

        # Add limit and offset
        params.extend([limit, offset])

        async with service.db.acquire() as conn:
            rows = await conn.fetch(f"""
                SELECT * FROM reaction_bot_logs
                WHERE {where_sql}
                ORDER BY timestamp DESC
                LIMIT ${param_count} OFFSET ${param_count + 1}
            """, *params)

            logs = [dict(row) for row in rows]

            return {
                "success": True,
                "logs": logs,
                "count": len(logs),
                "limit": limit,
                "offset": offset
            }

    except Exception as e:
        logger.error(f"❌ Error getting logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/batches", summary="Get batch processing history")
async def get_batches(
    limit: int = 20,
    offset: int = 0,
    status: Optional[str] = None,
    service: ReactionBotService = Depends(get_reaction_bot_service)
):
    """
    Get batch processing history.

    Args:
        limit: Maximum number of batches to return (default: 20, max: 100)
        offset: Pagination offset (default: 0)
        status: Filter by status ('pending', 'processing', 'completed', 'failed')

    Returns:
        List of batch records
    """
    try:
        if not service:
            raise HTTPException(status_code=503, detail="Service not available")

        if limit < 1 or limit > 100:
            raise HTTPException(status_code=400, detail="Limit must be between 1 and 100")

        where_sql = "1=1"
        params = []

        if status:
            where_sql = "status = $1"
            params.append(status)

        params.extend([limit, offset])
        param_offset = len(params) - 1

        async with service.db.acquire() as conn:
            rows = await conn.fetch(f"""
                SELECT * FROM reaction_bot_batches
                WHERE {where_sql}
                ORDER BY created_at DESC
                LIMIT ${param_offset} OFFSET ${param_offset + 1}
            """, *params)

            batches = [dict(row) for row in rows]

            return {
                "success": True,
                "batches": batches,
                "count": len(batches),
                "limit": limit,
                "offset": offset
            }

    except Exception as e:
        logger.error(f"❌ Error getting batches: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test-distribution", summary="Test reaction distribution (no actual reactions)")
async def test_distribution(
    article_count: int,
    reaction_percentage: int = 100
):
    """
    Test reaction distribution algorithm without sending actual reactions.

    This is useful for previewing how reactions will be distributed.

    Args:
        article_count: Number of articles
        reaction_percentage: Percentage (100=1x, 200=2x)

    Returns:
        Distribution preview
    """
    try:
        if article_count < 1 or article_count > 10000:
            raise HTTPException(status_code=400, detail="Article count must be between 1 and 10000")

        if reaction_percentage < 1 or reaction_percentage > 1000:
            raise HTTPException(status_code=400, detail="Reaction percentage must be between 1 and 1000")

        from reaction_bot_service import PoissonDistributor

        total_reactions = int(article_count * (reaction_percentage / 100))

        distributor = PoissonDistributor(article_count, total_reactions)
        distribution = distributor.distribute()

        # Calculate statistics
        reaction_counts = list(distribution.values())
        zero_count = sum(1 for count in reaction_counts if count == 0)
        non_zero_count = article_count - zero_count
        max_reactions = max(reaction_counts) if reaction_counts else 0
        min_reactions = min(reaction_counts) if reaction_counts else 0
        avg_reactions = sum(reaction_counts) / len(reaction_counts) if reaction_counts else 0

        # Create histogram
        from collections import Counter
        histogram = dict(Counter(reaction_counts))

        return {
            "success": True,
            "article_count": article_count,
            "total_reactions": total_reactions,
            "reaction_percentage": reaction_percentage,
            "statistics": {
                "zero_reactions": zero_count,
                "with_reactions": non_zero_count,
                "max_reactions": max_reactions,
                "min_reactions": min_reactions,
                "avg_reactions": round(avg_reactions, 2)
            },
            "histogram": histogram,
            "sample_distribution": {f"article_{i}": count for i, count in list(distribution.items())[:20]}
        }

    except Exception as e:
        logger.error(f"❌ Error testing distribution: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", summary="Health check")
async def health_check():
    """
    Health check endpoint.

    Returns:
        Health status
    """
    return {
        "success": True,
        "service": "reaction-bot",
        "status": "healthy",
        "timestamp": "2025-11-10"
    }


@router.get("/scheduler/status", summary="Get scheduler status")
async def get_scheduler_status():
    """
    Get scheduler status and next run time.

    Returns:
        Scheduler status information
    """
    try:
        from reaction_bot_scheduler import get_scheduler

        scheduler = get_scheduler()

        if not scheduler:
            return {
                "success": False,
                "message": "Scheduler not initialized",
                "running": False
            }

        status = scheduler.get_status()

        return {
            "success": True,
            **status
        }

    except Exception as e:
        logger.error(f"❌ Error getting scheduler status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scheduler/trigger", summary="Manually trigger hourly article fetch")
async def trigger_scheduler():
    """
    Manually trigger article fetch and processing (outside of schedule).

    Useful for testing or immediate execution.

    Returns:
        Execution result
    """
    try:
        from reaction_bot_scheduler import get_scheduler

        scheduler = get_scheduler()

        if not scheduler:
            raise HTTPException(
                status_code=503,
                detail="Scheduler not initialized"
            )

        # Trigger manual run
        await scheduler.trigger_manual_run()

        return {
            "success": True,
            "message": "Manual trigger completed successfully"
        }

    except Exception as e:
        logger.error(f"❌ Error triggering scheduler: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reactions/hourly-breakdown", summary="Get hourly reaction count breakdown")
async def get_hourly_reaction_breakdown(
    hours: int = 24,
    service: ReactionBotService = Depends(get_reaction_bot_service)
):
    """
    Get reaction count breakdown by hour from reaction_bot_logs.

    Args:
        hours: Number of hours to analyze (default: 24, max: 168)

    Returns:
        Hourly breakdown of reaction counts
    """
    try:
        if hours < 1 or hours > 168:
            raise HTTPException(status_code=400, detail="Hours must be between 1 and 168")

        from datetime import datetime, timedelta

        # Calculate time range
        end_time = datetime.now().replace(minute=0, second=0, microsecond=0)
        hourly_stats = []

        # Query reactions for each hour from reaction_bot_logs
        for i in range(hours):
            hour_end = end_time - timedelta(hours=i)
            hour_start = hour_end - timedelta(hours=1)

            # Query database for reactions in this hour
            conn = None
            try:
                from main import get_db_connection, return_db_connection
                conn = get_db_connection()

                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT COUNT(*) as reaction_count,
                               COUNT(CASE WHEN success = true THEN 1 END) as success_count,
                               COUNT(CASE WHEN success = false THEN 1 END) as failed_count
                        FROM reaction_bot_logs
                        WHERE timestamp >= %s AND timestamp < %s
                    """, (hour_start, hour_end))

                    result = cursor.fetchone()
                    reaction_count = result[0] if result else 0
                    success_count = result[1] if result else 0
                    failed_count = result[2] if result else 0

            except Exception as db_error:
                logger.warning(f"Database query failed for hour {i}: {db_error}")
                reaction_count = 0
                success_count = 0
                failed_count = 0
            finally:
                if conn:
                    return_db_connection(conn)

            # Format labels
            if i == 0:
                label = "Current hour"
            elif i == 1:
                label = "1h ago"
            else:
                label = f"{i}h ago"

            hour_label = hour_start.strftime("%H:00")

            hourly_stats.append({
                "hour": i,
                "hour_label": hour_label,
                "time_range": f"{hour_start.strftime('%H:%M')}-{hour_end.strftime('%H:%M')}",
                "count": reaction_count,
                "success_count": success_count,
                "failed_count": failed_count,
                "success_rate": (success_count / reaction_count * 100) if reaction_count > 0 else 0,
                "label": label,
                "start_time": hour_start.isoformat(),
                "end_time": hour_end.isoformat()
            })

        total_reactions = sum(stat["count"] for stat in hourly_stats)
        total_success = sum(stat["success_count"] for stat in hourly_stats)
        total_failed = sum(stat["failed_count"] for stat in hourly_stats)

        return {
            "success": True,
            "total_hours": hours,
            "total_reactions": total_reactions,
            "total_success": total_success,
            "total_failed": total_failed,
            "overall_success_rate": (total_success / total_reactions * 100) if total_reactions > 0 else 0,
            "hourly_breakdown": hourly_stats,
            "message": f"Fetched reaction breakdown for {hours} hours"
        }

    except Exception as e:
        logger.error(f"❌ Error getting hourly reaction breakdown: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reactions/by-kol", summary="Get reaction statistics grouped by KOL")
async def get_reactions_by_kol(
    hours: int = 24
):
    """
    Get reaction statistics grouped by KOL for the specified time range.

    Args:
        hours: Number of hours to analyze (default: 24, max: 168)

    Returns:
        Reaction counts per KOL with success/failure breakdown
    """
    try:
        if hours < 1 or hours > 168:
            raise HTTPException(status_code=400, detail="Hours must be between 1 and 168")

        from datetime import datetime, timedelta
        from main import get_db_connection, return_db_connection

        start_time = datetime.now() - timedelta(hours=hours)

        conn = None
        try:
            conn = get_db_connection()

            with conn.cursor() as cursor:
                # Get reaction counts grouped by KOL
                cursor.execute("""
                    SELECT
                        kol_serial,
                        COUNT(*) as total_reactions,
                        COUNT(CASE WHEN success = true THEN 1 END) as successful_reactions,
                        COUNT(CASE WHEN success = false THEN 1 END) as failed_reactions,
                        MIN(timestamp) as first_reaction_time,
                        MAX(timestamp) as last_reaction_time
                    FROM reaction_bot_logs
                    WHERE timestamp >= %s
                    GROUP BY kol_serial
                    ORDER BY total_reactions DESC
                """, (start_time,))

                results = cursor.fetchall()

                kol_stats = []
                total_reactions = 0
                total_successful = 0
                total_failed = 0

                for row in results:
                    kol_serial = row[0]
                    total = row[1]
                    successful = row[2]
                    failed = row[3]
                    first_time = row[4]
                    last_time = row[5]

                    total_reactions += total
                    total_successful += successful
                    total_failed += failed

                    success_rate = (successful / total * 100) if total > 0 else 0

                    kol_stats.append({
                        "kol_serial": kol_serial,
                        "total_reactions": total,
                        "successful_reactions": successful,
                        "failed_reactions": failed,
                        "success_rate": round(success_rate, 2),
                        "first_reaction_time": first_time.isoformat() if first_time else None,
                        "last_reaction_time": last_time.isoformat() if last_time else None
                    })

        finally:
            if conn:
                return_db_connection(conn)

        return {
            "success": True,
            "hours_analyzed": hours,
            "total_kols": len(kol_stats),
            "total_reactions": total_reactions,
            "total_successful": total_successful,
            "total_failed": total_failed,
            "overall_success_rate": round((total_successful / total_reactions * 100) if total_reactions > 0 else 0, 2),
            "kol_statistics": kol_stats,
            "message": f"Fetched reaction statistics for {len(kol_stats)} KOLs over {hours} hours"
        }

    except Exception as e:
        logger.error(f"❌ Error getting KOL reaction statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/fetch-articles/hourly-breakdown", summary="Get hourly article count breakdown")
async def get_hourly_article_breakdown(
    hours: int = 24
):
    """
    Get article count breakdown by hour.

    Fetches articles for the specified time range and groups them by hour.

    Args:
        hours: Number of hours to analyze (default: 24, max: 168)

    Returns:
        Hourly breakdown of article counts
    """
    try:
        if hours < 1 or hours > 168:
            raise HTTPException(status_code=400, detail="Hours must be between 1 and 168")

        from article_stream_fetcher import ArticleStreamFetcher
        from datetime import datetime, timedelta

        fetcher = ArticleStreamFetcher()

        # Fetch all articles for past N hours with hour-by-hour breakdown
        hourly_stats = []
        end_time = datetime.now().replace(minute=0, second=0, microsecond=0)

        for i in range(hours):
            hour_end = end_time - timedelta(hours=i)
            hour_start = hour_end - timedelta(hours=1)

            # Fetch articles for this specific hour
            status_code, article_ids = fetcher.fetch_hourly_articles(
                hours_back=1,  # Not used when custom times provided
                custom_start_time=hour_start,
                custom_end_time=hour_end
            )

            # Format hour label (e.g., "14:00-15:00" or "1h ago")
            if i == 0:
                label = "Current hour"
            elif i == 1:
                label = "1h ago"
            else:
                label = f"{i}h ago"

            hour_label = hour_start.strftime("%H:00")

            hourly_stats.append({
                "hour": i,
                "hour_label": hour_label,
                "time_range": f"{hour_start.strftime('%H:%M')}-{hour_end.strftime('%H:%M')}",
                "count": len(article_ids) if status_code == 200 else 0,
                "label": label,
                "start_time": hour_start.isoformat(),
                "end_time": hour_end.isoformat()
            })

        total_articles = sum(stat["count"] for stat in hourly_stats)

        return {
            "success": True,
            "total_hours": hours,
            "total_articles": total_articles,
            "hourly_breakdown": hourly_stats,
            "message": f"Fetched breakdown for {hours} hours"
        }

    except Exception as e:
        logger.error(f"❌ Error getting hourly breakdown: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/fetch-articles", summary="Fetch new article IDs")
async def fetch_new_articles(
    hours_back: int = 1
):
    """
    Fetch new article IDs from CMoney API without processing.

    Args:
        hours_back: Number of hours to look back (default: 1)

    Returns:
        List of article IDs
    """
    try:
        from article_stream_fetcher import ArticleStreamFetcher

        fetcher = ArticleStreamFetcher()
        status_code, article_ids = fetcher.fetch_hourly_articles(hours_back=hours_back)

        if status_code == 200:
            return {
                "success": True,
                "article_count": len(article_ids),
                "article_ids": article_ids[:100],  # Return first 100 for preview
                "total_count": len(article_ids),
                "message": f"Successfully fetched {len(article_ids)} articles"
            }
        else:
            return {
                "success": False,
                "status_code": status_code,
                "article_count": 0,
                "article_ids": [],
                "message": f"Failed to fetch articles (status: {status_code})"
            }

    except Exception as e:
        logger.error(f"❌ Error fetching articles: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# Hourly Reaction Statistics Endpoints
# ============================================

@router.post("/hourly-task/run", summary="Run hourly reaction task manually")
async def run_hourly_task(
    kol_serials: Optional[List[int]] = None
):
    """
    Manually trigger hourly reaction task.

    This will:
    1. Fetch past hour articles from Kafka stream
    2. Use KOL pool to like articles (with rotation)
    3. Save statistics to hourly_reaction_stats table

    Args:
        kol_serials: Optional list of KOL serials to use (None = use all active KOLs)

    Returns:
        Task execution result with statistics
    """
    try:
        from main import get_db_connection, return_db_connection
        from hourly_reaction_service import HourlyReactionService
        from cmoney_reaction_client import CMoneyReactionClient
        from psycopg2 import pool
        import os

        # Create simple connection pool
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise HTTPException(status_code=500, detail="DATABASE_URL not configured")

        import urllib.parse
        parsed_url = urllib.parse.urlparse(database_url)

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
            cmoney_client = CMoneyReactionClient()
            service = HourlyReactionService(db_pool, cmoney_client)

            # Run hourly task
            await service.run_hourly_task(kol_serials=kol_serials)

            return {
                "success": True,
                "message": "Hourly task completed successfully",
                "kol_serials_used": kol_serials if kol_serials else "all active KOLs"
            }

        finally:
            db_pool.closeall()

    except Exception as e:
        logger.error(f"❌ Error running hourly task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/hourly-stats", summary="Get hourly reaction statistics")
async def get_hourly_stats(
    limit: int = 24,
    offset: int = 0
):
    """
    Get hourly reaction statistics from hourly_reaction_stats table.

    Args:
        limit: Maximum number of records to return (default: 24, max: 168)
        offset: Pagination offset (default: 0)

    Returns:
        List of hourly statistics records
    """
    try:
        if limit < 1 or limit > 168:
            raise HTTPException(status_code=400, detail="Limit must be between 1 and 168")

        from main import get_db_connection, return_db_connection

        conn = None
        try:
            conn = get_db_connection()

            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT
                        id,
                        hour_start,
                        hour_end,
                        total_new_articles,
                        total_like_attempts,
                        successful_likes,
                        unique_articles_liked,
                        like_success_rate,
                        kol_pool_serials,
                        created_at,
                        updated_at
                    FROM hourly_reaction_stats
                    ORDER BY hour_start DESC
                    LIMIT %s OFFSET %s
                """, (limit, offset))

                rows = cursor.fetchall()

                stats = []
                for row in rows:
                    stats.append({
                        "id": row[0],
                        "hour_start": row[1].isoformat() if row[1] else None,
                        "hour_end": row[2].isoformat() if row[2] else None,
                        "total_new_articles": row[3],
                        "total_like_attempts": row[4],
                        "successful_likes": row[5],
                        "unique_articles_liked": row[6],
                        "like_success_rate": float(row[7]) if row[7] else 0,
                        "kol_pool_serials": row[8],
                        "created_at": row[9].isoformat() if row[9] else None,
                        "updated_at": row[10].isoformat() if row[10] else None
                    })

                # Get total count
                cursor.execute("SELECT COUNT(*) FROM hourly_reaction_stats")
                total_count = cursor.fetchone()[0]

        finally:
            if conn:
                return_db_connection(conn)

        return {
            "success": True,
            "stats": stats,
            "count": len(stats),
            "total_count": total_count,
            "limit": limit,
            "offset": offset,
            "message": f"Fetched {len(stats)} hourly statistics records"
        }

    except Exception as e:
        logger.error(f"❌ Error getting hourly stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/hourly-stats/latest", summary="Get latest hourly statistics")
async def get_latest_hourly_stats():
    """
    Get the most recent hourly statistics record.

    Returns:
        Latest hourly statistics record
    """
    try:
        from main import get_db_connection, return_db_connection

        conn = None
        try:
            conn = get_db_connection()

            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT
                        id,
                        hour_start,
                        hour_end,
                        total_new_articles,
                        total_like_attempts,
                        successful_likes,
                        unique_articles_liked,
                        like_success_rate,
                        kol_pool_serials,
                        article_ids,
                        created_at,
                        updated_at
                    FROM hourly_reaction_stats
                    ORDER BY hour_start DESC
                    LIMIT 1
                """)

                row = cursor.fetchone()

                if not row:
                    return {
                        "success": False,
                        "message": "No statistics records found"
                    }

                stats = {
                    "id": row[0],
                    "hour_start": row[1].isoformat() if row[1] else None,
                    "hour_end": row[2].isoformat() if row[2] else None,
                    "total_new_articles": row[3],
                    "total_like_attempts": row[4],
                    "successful_likes": row[5],
                    "unique_articles_liked": row[6],
                    "like_success_rate": float(row[7]) if row[7] else 0,
                    "kol_pool_serials": row[8],
                    "article_ids_count": len(row[9]) if row[9] else 0,
                    "article_ids_sample": row[9][:10] if row[9] else [],
                    "created_at": row[10].isoformat() if row[10] else None,
                    "updated_at": row[11].isoformat() if row[11] else None
                }

        finally:
            if conn:
                return_db_connection(conn)

        return {
            "success": True,
            "stats": stats,
            "message": "Fetched latest hourly statistics"
        }

    except Exception as e:
        logger.error(f"❌ Error getting latest hourly stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/debug/db-tables", summary="List all database tables")
async def list_db_tables():
    """
    List all database tables with row counts (for debugging).

    Returns:
        List of tables with their row counts and sample columns
    """
    try:
        from main import get_db_connection, return_db_connection

        conn = None
        try:
            conn = get_db_connection()

            with conn.cursor() as cursor:
                # Get all tables
                cursor.execute("""
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    ORDER BY table_name
                """)

                tables_data = []
                for (table_name,) in cursor.fetchall():
                    # Get row count
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = cursor.fetchone()[0]

                    # Get column names
                    cursor.execute(f"""
                        SELECT column_name
                        FROM information_schema.columns
                        WHERE table_name = '{table_name}'
                        ORDER BY ordinal_position
                        LIMIT 5
                    """)
                    columns = [row[0] for row in cursor.fetchall()]

                    tables_data.append({
                        "table_name": table_name,
                        "row_count": count,
                        "status": "has_data" if count > 0 else "empty",
                        "sample_columns": columns
                    })

        finally:
            if conn:
                return_db_connection(conn)

        return {
            "success": True,
            "tables": tables_data,
            "total_tables": len(tables_data),
            "message": f"Found {len(tables_data)} tables"
        }

    except Exception as e:
        logger.error(f"❌ Error listing tables: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/hourly-stats/summary", summary="Get hourly statistics summary")
async def get_hourly_stats_summary(
    hours: int = 24
):
    """
    Get aggregated summary of hourly statistics.

    Args:
        hours: Number of hours to include in summary (default: 24, max: 168)

    Returns:
        Aggregated statistics summary
    """
    try:
        if hours < 1 or hours > 168:
            raise HTTPException(status_code=400, detail="Hours must be between 1 and 168")

        from main import get_db_connection, return_db_connection
        from datetime import datetime, timedelta

        cutoff_time = datetime.now() - timedelta(hours=hours)

        conn = None
        try:
            conn = get_db_connection()

            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT
                        COUNT(*) as total_hours,
                        SUM(total_new_articles) as total_articles,
                        SUM(total_like_attempts) as total_attempts,
                        SUM(successful_likes) as total_success,
                        SUM(unique_articles_liked) as total_unique_articles,
                        AVG(like_success_rate) as avg_success_rate,
                        MIN(hour_start) as earliest_hour,
                        MAX(hour_start) as latest_hour
                    FROM hourly_reaction_stats
                    WHERE hour_start >= %s
                """, (cutoff_time,))

                row = cursor.fetchone()

                if not row or row[0] == 0:
                    return {
                        "success": False,
                        "message": f"No statistics found for past {hours} hours"
                    }

                summary = {
                    "hours_analyzed": hours,
                    "total_hours_with_data": row[0],
                    "total_new_articles": row[1] or 0,
                    "total_like_attempts": row[2] or 0,
                    "total_successful_likes": row[3] or 0,
                    "total_unique_articles_liked": row[4] or 0,
                    "average_success_rate": round(float(row[5]) if row[5] else 0, 2),
                    "earliest_hour": row[6].isoformat() if row[6] else None,
                    "latest_hour": row[7].isoformat() if row[7] else None,
                    "articles_per_hour": round((row[1] or 0) / (row[0] or 1), 2),
                    "likes_per_hour": round((row[3] or 0) / (row[0] or 1), 2)
                }

        finally:
            if conn:
                return_db_connection(conn)

        return {
            "success": True,
            "summary": summary,
            "message": f"Fetched summary for past {hours} hours"
        }

    except Exception as e:
        logger.error(f"❌ Error getting hourly stats summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))
