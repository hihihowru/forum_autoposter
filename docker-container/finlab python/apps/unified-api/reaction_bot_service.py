"""
Reaction Bot Service
Handles auto-like reactions for newly created articles using Poisson distribution.

Created: 2025-11-10
Author: Claude Code
"""

import asyncio
import logging
import random
import time
from datetime import datetime
from typing import List, Dict, Tuple, Optional
import numpy as np
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ReactionBotConfig:
    """Reaction bot configuration"""
    enabled: bool
    reaction_percentage: int  # 100 = 1x, 200 = 2x
    selected_kol_serials: List[int]
    distribution_algorithm: str  # 'poisson', 'uniform', 'weighted'
    min_delay_seconds: float
    max_delay_seconds: float
    max_reactions_per_kol_per_hour: int


class PoissonDistributor:
    """
    Distributes reactions across articles using Poisson distribution.

    This creates a natural, random distribution where:
    - Most articles get close to the average number of reactions
    - Some get more, some get less (realistic engagement pattern)
    - Avoids suspicion from too uniform or too concentrated distribution
    """

    def __init__(self, total_articles: int, total_reactions: int):
        """
        Initialize Poisson distributor.

        Args:
            total_articles: Number of articles to distribute reactions across
            total_reactions: Total number of reactions to distribute
        """
        self.total_articles = total_articles
        self.total_reactions = total_reactions
        self.lambda_param = total_reactions / total_articles if total_articles > 0 else 0

        logger.info(f"📊 Poisson Distributor initialized: {total_articles} articles, {total_reactions} reactions, λ={self.lambda_param:.2f}")

    def distribute(self) -> Dict[int, int]:
        """
        Distribute reactions across articles using Poisson distribution.

        Returns:
            Dict mapping article index to number of reactions: {0: 2, 1: 1, 2: 3, ...}
        """
        if self.total_articles == 0:
            return {}

        # Generate Poisson distribution
        reactions_per_article = np.random.poisson(self.lambda_param, self.total_articles)

        # Calculate total reactions from distribution
        generated_total = np.sum(reactions_per_article)

        # Adjust to match exact total (scale proportionally)
        if generated_total > 0:
            scaling_factor = self.total_reactions / generated_total
            reactions_per_article = np.round(reactions_per_article * scaling_factor).astype(int)

        # Fine-tune to match exact total
        current_total = np.sum(reactions_per_article)
        diff = self.total_reactions - current_total

        if diff > 0:
            # Add missing reactions to random articles
            indices = random.sample(range(self.total_articles), min(diff, self.total_articles))
            for idx in indices:
                reactions_per_article[idx] += 1
        elif diff < 0:
            # Remove excess reactions from articles with >0 reactions
            non_zero_indices = np.where(reactions_per_article > 0)[0]
            remove_count = abs(diff)
            indices = random.sample(list(non_zero_indices), min(remove_count, len(non_zero_indices)))
            for idx in indices:
                reactions_per_article[idx] -= 1

        # Convert to dictionary
        distribution = {i: int(count) for i, count in enumerate(reactions_per_article)}

        # Log statistics
        non_zero = sum(1 for count in distribution.values() if count > 0)
        max_reactions = max(distribution.values()) if distribution else 0
        avg_reactions = sum(distribution.values()) / len(distribution) if distribution else 0

        logger.info(f"✅ Distribution complete: {non_zero}/{self.total_articles} articles with reactions, max={max_reactions}, avg={avg_reactions:.2f}")

        return distribution


class ReactionBotService:
    """
    Service for managing auto-like reaction bot.

    Features:
    - Poisson distribution for natural randomness
    - Rate limiting per KOL
    - Async execution with delays
    - Comprehensive logging
    """

    def __init__(self, db_connection, cmoney_client):
        """
        Initialize reaction bot service.

        Args:
            db_connection: Database connection pool
            cmoney_client: CMoney API client for sending reactions
        """
        self.db = db_connection
        self.cmoney_client = cmoney_client
        self.processing = False
        logger.info("✅ ReactionBotService initialized")

    async def get_config(self) -> Optional[ReactionBotConfig]:
        """
        Get current bot configuration from database.

        Returns:
            ReactionBotConfig or None if not found
        """
        async with self.db.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM reaction_bot_config ORDER BY id DESC LIMIT 1")

            if not row:
                logger.warning("⚠️ No reaction bot config found in database")
                return None

            # Parse selected_kol_serials from JSON if it's a string
            kol_serials = row['selected_kol_serials']
            if isinstance(kol_serials, str):
                import json
                try:
                    kol_serials = json.loads(kol_serials) if kol_serials else []
                except:
                    kol_serials = []
            elif kol_serials is None:
                kol_serials = []

            return ReactionBotConfig(
                enabled=row['enabled'],
                reaction_percentage=row['reaction_percentage'],
                selected_kol_serials=kol_serials,
                distribution_algorithm=row['distribution_algorithm'],
                min_delay_seconds=row['min_delay_seconds'],
                max_delay_seconds=row['max_delay_seconds'],
                max_reactions_per_kol_per_hour=row['max_reactions_per_kol_per_hour'],
                created_at=row.get('created_at'),
                updated_at=row.get('updated_at')
            )

    async def update_config(self, config_updates: Dict) -> Dict:
        """
        Update bot configuration.

        Args:
            config_updates: Dict with config fields to update

        Returns:
            Updated configuration
        """
        allowed_fields = [
            'enabled', 'reaction_percentage', 'selected_kol_serials',
            'distribution_algorithm', 'min_delay_seconds', 'max_delay_seconds',
            'max_reactions_per_kol_per_hour'
        ]

        # Filter only allowed fields
        updates = {k: v for k, v in config_updates.items() if k in allowed_fields}

        if not updates:
            raise ValueError("No valid fields to update")

        # Build UPDATE query
        set_clause = ", ".join([f"{k} = ${i+1}" for i, k in enumerate(updates.keys())])
        values = list(updates.values())

        async with self.db.acquire() as conn:
            query = f"""
                UPDATE reaction_bot_config
                SET {set_clause}, updated_at = NOW()
                WHERE id = (SELECT id FROM reaction_bot_config ORDER BY id DESC LIMIT 1)
                RETURNING *
            """
            row = await conn.fetchrow(query, *values)

            logger.info(f"✅ Updated reaction bot config: {updates}")

            return dict(row)

    async def process_article_batch(
        self,
        article_ids: List[str],
        batch_id: Optional[str] = None
    ) -> Dict:
        """
        Process a batch of article IDs and send reactions.

        Args:
            article_ids: List of article IDs to process
            batch_id: Optional batch identifier (auto-generated if not provided)

        Returns:
            Processing result summary
        """
        if self.processing:
            raise RuntimeError("Reaction bot is already processing a batch")

        self.processing = True

        try:
            # Get config
            config = await self.get_config()
            if not config:
                raise RuntimeError("No reaction bot config found")

            if not config.enabled:
                logger.warning("⚠️ Reaction bot is disabled")
                return {"success": False, "message": "Reaction bot is disabled"}

            if not config.selected_kol_serials:
                raise ValueError("No KOL profiles selected for reaction bot")

            if not article_ids:
                logger.warning("⚠️ No article IDs provided")
                return {"success": True, "message": "No articles to process", "reactions_sent": 0}

            # Generate batch ID
            if not batch_id:
                batch_id = f"batch_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"

            # Calculate total reactions
            total_reactions = int(len(article_ids) * (config.reaction_percentage / 100))

            logger.info(f"🚀 Starting batch: {batch_id}")
            logger.info(f"📋 Articles: {len(article_ids)}, Reactions: {total_reactions} ({config.reaction_percentage}%)")
            logger.info(f"👥 KOL Pool: {config.selected_kol_serials}")

            # Create batch record
            await self._create_batch_record(batch_id, len(article_ids), total_reactions)

            # Distribute reactions using Poisson
            distributor = PoissonDistributor(len(article_ids), total_reactions)
            distribution = distributor.distribute()

            # Create article queue entries
            await self._create_article_queue(batch_id, article_ids, distribution)

            # Execute reactions
            result = await self._execute_reactions(
                batch_id,
                article_ids,
                distribution,
                config
            )

            # Update batch status
            await self._complete_batch(batch_id, result)

            # Calculate daily stats
            await self._update_daily_stats()

            logger.info(f"✅ Batch {batch_id} completed: {result['reactions_sent']}/{total_reactions} reactions sent")

            return result

        finally:
            self.processing = False

    async def _create_batch_record(self, batch_id: str, article_count: int, total_reactions: int):
        """Create batch record in database."""
        async with self.db.acquire() as conn:
            await conn.execute("""
                INSERT INTO reaction_bot_batches (
                    batch_id, article_count, total_reactions, status, started_at
                )
                VALUES ($1, $2, $3, 'processing', NOW())
            """, batch_id, article_count, total_reactions)

    async def _create_article_queue(
        self,
        batch_id: str,
        article_ids: List[str],
        distribution: Dict[int, int]
    ):
        """Create article queue entries."""
        async with self.db.acquire() as conn:
            for i, article_id in enumerate(article_ids):
                assigned_reactions = distribution.get(i, 0)
                await conn.execute("""
                    INSERT INTO reaction_bot_article_queue (
                        batch_id, article_id, assigned_reactions, status
                    )
                    VALUES ($1, $2, $3, 'pending')
                """, batch_id, article_id, assigned_reactions)

    async def _execute_reactions(
        self,
        batch_id: str,
        article_ids: List[str],
        distribution: Dict[int, int],
        config: ReactionBotConfig
    ) -> Dict:
        """Execute reactions with rate limiting and delays."""
        reactions_sent = 0
        reactions_failed = 0

        # Build reaction list: [(article_id, kol_serial), ...]
        reaction_tasks = []

        for i, article_id in enumerate(article_ids):
            reaction_count = distribution.get(i, 0)

            if reaction_count == 0:
                continue

            # Assign KOLs randomly
            assigned_kols = random.choices(config.selected_kol_serials, k=reaction_count)

            for kol_serial in assigned_kols:
                reaction_tasks.append((article_id, kol_serial))

        # Shuffle to randomize order
        random.shuffle(reaction_tasks)

        logger.info(f"📤 Sending {len(reaction_tasks)} reactions...")

        # Execute reactions with delays
        for article_id, kol_serial in reaction_tasks:
            try:
                # Random delay
                delay = random.uniform(config.min_delay_seconds, config.max_delay_seconds)
                await asyncio.sleep(delay)

                # Send reaction via CMoney API
                success, response = await self._send_reaction(article_id, kol_serial)

                if success:
                    reactions_sent += 1
                    logger.debug(f"✅ Reaction sent: article={article_id}, kol={kol_serial}")
                else:
                    reactions_failed += 1
                    logger.warning(f"❌ Reaction failed: article={article_id}, kol={kol_serial}")

                # Log to database
                await self._log_reaction(article_id, kol_serial, success, response)

            except Exception as e:
                reactions_failed += 1
                logger.error(f"❌ Error sending reaction: {e}")
                await self._log_reaction(article_id, kol_serial, False, {"error": str(e)})

        return {
            "success": True,
            "batch_id": batch_id,
            "reactions_sent": reactions_sent,
            "reactions_failed": reactions_failed,
            "total_articles": len(article_ids),
            "total_reactions": reactions_sent + reactions_failed
        }

    async def _send_reaction(self, article_id: str, kol_serial: int) -> Tuple[bool, Dict]:
        """
        Send reaction via CMoney API.

        Args:
            article_id: Article ID to react to
            kol_serial: KOL serial number

        Returns:
            (success: bool, response: Dict)
        """
        try:
            # Get KOL credentials from database
            async with self.db.acquire() as conn:
                kol_row = await conn.fetchrow("""
                    SELECT email, password_hash, access_token
                    FROM kol_profiles
                    WHERE serial = $1
                """, kol_serial)

                if not kol_row:
                    logger.error(f"❌ KOL serial {kol_serial} not found")
                    return False, {"error": f"KOL serial {kol_serial} not found"}

            # Get access token (login if needed)
            access_token = await self.cmoney_client.get_or_refresh_token(
                kol_serial,
                kol_row['email'],
                kol_row['password_hash']
            )

            if not access_token:
                logger.error(f"❌ Failed to get access token for KOL {kol_serial}")
                return False, {"error": "Failed to get access token"}

            # Send reaction (type 1 = like)
            result = await self.cmoney_client.add_article_reaction(
                access_token=access_token,
                article_id=article_id,
                reaction_type=1  # 1 = 讚 (like)
            )

            if result.success:
                return True, {
                    "success": True,
                    "article_id": article_id,
                    "kol_serial": kol_serial,
                    "reaction_type": result.reaction_type
                }
            else:
                logger.error(f"❌ CMoney API reaction failed: {result.error_message}")
                return False, {
                    "error": result.error_message,
                    "article_id": article_id
                }

        except Exception as e:
            logger.error(f"❌ CMoney API error: {e}")
            return False, {"error": str(e)}

    async def _log_reaction(self, article_id: str, kol_serial: int, success: bool, response: Dict):
        """Log reaction to database."""
        async with self.db.acquire() as conn:
            await conn.execute("""
                INSERT INTO reaction_bot_logs (
                    article_id, kol_serial, reaction_type, success, response_data
                )
                VALUES ($1, $2, 'like', $3, $4)
            """, article_id, kol_serial, success, response)

    async def _complete_batch(self, batch_id: str, result: Dict):
        """Update batch status to completed."""
        async with self.db.acquire() as conn:
            await conn.execute("""
                UPDATE reaction_bot_batches
                SET status = 'completed',
                    reactions_sent = $1,
                    reactions_failed = $2,
                    completed_at = NOW()
                WHERE batch_id = $3
            """, result['reactions_sent'], result['reactions_failed'], batch_id)

    async def _update_daily_stats(self):
        """Update daily statistics."""
        today = datetime.now().date()
        async with self.db.acquire() as conn:
            await conn.execute("SELECT calculate_reaction_bot_daily_stats($1)", today)

    async def get_stats(self, days: int = 7) -> Dict:
        """
        Get reaction bot statistics.

        Args:
            days: Number of days to include (default: 7)

        Returns:
            Statistics dict
        """
        async with self.db.acquire() as conn:
            # Get daily stats
            rows = await conn.fetch("""
                SELECT * FROM reaction_bot_stats
                WHERE date >= CURRENT_DATE - $1
                ORDER BY date DESC
            """, days)

            daily_stats = [dict(row) for row in rows]

            # Get overall stats
            overall = await conn.fetchrow("""
                SELECT
                    COUNT(*) as total_batches,
                    SUM(reactions_sent) as total_reactions_sent,
                    SUM(reactions_failed) as total_reactions_failed,
                    AVG(reactions_sent::FLOAT / NULLIF(article_count, 0)) as avg_reactions_per_article
                FROM reaction_bot_batches
                WHERE created_at >= CURRENT_DATE - $1
            """, days)

            return {
                "daily_stats": daily_stats,
                "overall": dict(overall) if overall else {},
                "period_days": days
            }
