"""
Reaction Bot Scheduler
Automated hourly scheduler that fetches new articles and triggers reaction bot

Created: 2025-11-10
Author: Claude Code
"""

import asyncio
import logging
from datetime import datetime
from typing import Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from article_stream_fetcher import ArticleStreamFetcher
from reaction_bot_service import ReactionBotService

logger = logging.getLogger(__name__)


class ReactionBotScheduler:
    """
    Scheduler service that:
    1. Fetches new article IDs every hour
    2. Automatically triggers reaction bot to process them
    3. Logs all activity
    """

    def __init__(
        self,
        reaction_bot_service: ReactionBotService,
        cmoney_cookie: Optional[str] = None
    ):
        """
        Initialize scheduler.

        Args:
            reaction_bot_service: ReactionBotService instance
            cmoney_cookie: CMoney API session cookie
        """
        self.reaction_bot_service = reaction_bot_service
        self.article_fetcher = ArticleStreamFetcher(cookie_session=cmoney_cookie)
        self.scheduler = AsyncIOScheduler()
        self.running = False

        logger.info("✅ ReactionBotScheduler initialized")

    async def fetch_and_process_articles(self):
        """
        Main scheduled task: Fetch articles and trigger reaction bot.

        This runs every hour automatically.
        """
        try:
            now = datetime.now()
            logger.info(f"🕐 Starting hourly article fetch at {now}")

            # Check if reaction bot is enabled
            config = await self.reaction_bot_service.get_config()

            if not config:
                logger.warning("⚠️ No reaction bot config found, skipping")
                return

            if not config.enabled:
                logger.info("ℹ️ Reaction bot is disabled, skipping article processing")
                return

            # Fetch new article IDs
            logger.info("📥 Fetching new article IDs from CMoney API...")
            status_code, article_ids = self.article_fetcher.fetch_hourly_articles(hours_back=1)

            if status_code != 200:
                logger.error(f"❌ Failed to fetch articles (status: {status_code})")
                return

            if not article_ids:
                logger.info("ℹ️ No new articles found in the past hour")
                return

            logger.info(f"✅ Found {len(article_ids)} new articles")

            # Generate batch ID
            batch_id = f"auto_batch_{now.strftime('%Y-%m-%d_%H-%M-%S')}"

            # Trigger reaction bot
            logger.info(f"🚀 Triggering reaction bot with batch_id: {batch_id}")

            result = await self.reaction_bot_service.process_article_batch(
                article_ids=article_ids,
                batch_id=batch_id
            )

            if result['success']:
                logger.info(f"✅ Batch processing completed successfully")
                logger.info(f"📊 Reactions sent: {result['reactions_sent']}/{result['total_reactions']}")
                logger.info(f"❌ Reactions failed: {result['reactions_failed']}")
            else:
                logger.error(f"❌ Batch processing failed: {result.get('message')}")

        except Exception as e:
            logger.error(f"❌ Error in fetch_and_process_articles: {e}", exc_info=True)

    def start(self, cron_expression: str = "0 * * * *"):
        """
        Start the scheduler.

        Args:
            cron_expression: Cron expression (default: "0 * * * *" = every hour at minute 0)

        Cron expressions:
            - "0 * * * *"    = Every hour at minute 0 (12:00, 13:00, 14:00, ...)
            - "*/30 * * * *" = Every 30 minutes
            - "0 9-17 * * *" = Every hour from 9 AM to 5 PM
            - "0 12,18 * * *" = At 12:00 PM and 6:00 PM
        """
        if self.running:
            logger.warning("⚠️ Scheduler is already running")
            return

        try:
            # Add job to scheduler
            self.scheduler.add_job(
                self.fetch_and_process_articles,
                trigger=CronTrigger.from_crontab(cron_expression),
                id='reaction_bot_hourly',
                name='Reaction Bot Hourly Article Processing',
                replace_existing=True,
                max_instances=1  # Prevent overlapping executions
            )

            # Start scheduler
            self.scheduler.start()
            self.running = True

            logger.info(f"✅ Scheduler started with cron: {cron_expression}")
            logger.info(f"📅 Next run: {self.scheduler.get_job('reaction_bot_hourly').next_run_time}")

        except Exception as e:
            logger.error(f"❌ Failed to start scheduler: {e}")
            raise

    def stop(self):
        """Stop the scheduler."""
        if not self.running:
            logger.warning("⚠️ Scheduler is not running")
            return

        try:
            self.scheduler.shutdown(wait=False)
            self.running = False
            logger.info("✅ Scheduler stopped")
        except Exception as e:
            logger.error(f"❌ Error stopping scheduler: {e}")

    def get_next_run_time(self):
        """Get next scheduled run time."""
        if not self.running:
            return None

        try:
            job = self.scheduler.get_job('reaction_bot_hourly')
            return job.next_run_time if job else None
        except Exception:
            return None

    async def trigger_manual_run(self):
        """
        Manually trigger article fetch and processing (outside of schedule).

        Useful for testing or manual execution.
        """
        logger.info("🔧 Manual trigger requested")
        await self.fetch_and_process_articles()

    def is_running(self) -> bool:
        """Check if scheduler is running."""
        return self.running

    def get_status(self) -> dict:
        """
        Get scheduler status.

        Returns:
            Dict with status information
        """
        if not self.running:
            return {
                "running": False,
                "next_run_time": None,
                "job_count": 0
            }

        job = self.scheduler.get_job('reaction_bot_hourly')

        return {
            "running": True,
            "next_run_time": str(job.next_run_time) if job else None,
            "job_count": len(self.scheduler.get_jobs()),
            "job_details": {
                "id": job.id,
                "name": job.name,
                "trigger": str(job.trigger)
            } if job else None
        }


# Global scheduler instance (to be initialized in main.py)
_scheduler_instance: Optional[ReactionBotScheduler] = None


def get_scheduler() -> Optional[ReactionBotScheduler]:
    """Get global scheduler instance."""
    return _scheduler_instance


def set_scheduler(scheduler: ReactionBotScheduler):
    """Set global scheduler instance."""
    global _scheduler_instance
    _scheduler_instance = scheduler


# Standalone script for manual testing
async def test_scheduler():
    """Test scheduler functionality."""
    from reaction_bot_service import ReactionBotService
    import asyncpg

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("=" * 60)
    print("Reaction Bot Scheduler - Test Run")
    print("=" * 60)

    # Create mock database connection
    # In production, replace with actual connection
    db_connection = None  # TODO: Replace with real DB connection

    # Create mock CMoney client
    # In production, replace with actual client
    cmoney_client = None  # TODO: Replace with real CMoney client

    # Initialize services
    reaction_bot_service = ReactionBotService(db_connection, cmoney_client)

    # Initialize scheduler
    scheduler = ReactionBotScheduler(reaction_bot_service)

    # Test manual trigger
    print("\n📋 Testing manual trigger...")
    await scheduler.trigger_manual_run()

    print("\n" + "=" * 60)
    print("Test completed")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_scheduler())
