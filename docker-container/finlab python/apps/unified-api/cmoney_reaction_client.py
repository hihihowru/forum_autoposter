"""
CMoney Reaction Client for Reaction Bot
Manages authentication and token caching for multiple KOL accounts

Created: 2025-11-11
Author: Claude Code
"""

import logging
from typing import Dict, Optional
from datetime import datetime, timedelta
from cmoney_client import CMoneyClient, LoginCredentials, AccessToken, ReactionResult

logger = logging.getLogger(__name__)


class CMoneyReactionClient:
    """
    Wrapper for CMoney client with token management for multiple KOL accounts.

    Features:
    - Token caching per KOL serial
    - Automatic token refresh on expiry
    - Async-compatible wrapper for sync CMoney client
    """

    def __init__(self):
        """Initialize reaction client with CMoney API client."""
        self.cmoney_client = CMoneyClient()
        self._token_cache: Dict[int, AccessToken] = {}  # kol_serial -> AccessToken
        logger.info("✅ CMoneyReactionClient initialized")

    async def get_or_refresh_token(
        self,
        kol_serial: int,
        email: str,
        password: str
    ) -> Optional[str]:
        """
        Get cached access token or login to get new one.

        Args:
            kol_serial: KOL serial number
            email: KOL email
            password: KOL password

        Returns:
            Access token string or None if login fails
        """
        try:
            # Check cache
            if kol_serial in self._token_cache:
                cached_token = self._token_cache[kol_serial]
                if not cached_token.is_expired:
                    logger.debug(f"✅ Using cached token for KOL {kol_serial}")
                    return cached_token.token

            # Login to get new token
            logger.info(f"🔐 Logging in KOL {kol_serial} ({email})")
            credentials = LoginCredentials(email=email, password=password)
            token = await self.cmoney_client.login(credentials)

            # Cache token
            self._token_cache[kol_serial] = token
            logger.info(f"✅ Login successful for KOL {kol_serial}, token expires at {token.expires_at}")

            return token.token

        except Exception as e:
            logger.error(f"❌ Login failed for KOL {kol_serial}: {e}")
            return None

    async def add_article_reaction(
        self,
        access_token: str,
        article_id: str,
        reaction_type: int = 1
    ) -> ReactionResult:
        """
        Add reaction to article.

        Args:
            access_token: CMoney access token
            article_id: Article ID
            reaction_type: Reaction type (1=讚, 3=哈, 4=賺, 5=哇, 6=嗚嗚, 7=真的嗎, 8=怒)

        Returns:
            ReactionResult
        """
        try:
            result = await self.cmoney_client.add_article_reaction(
                access_token=access_token,
                article_id=article_id,
                reaction_type=reaction_type
            )

            if result.success:
                logger.debug(f"✅ Reaction added to article {article_id}, type={reaction_type}")
            else:
                logger.warning(f"⚠️ Failed to add reaction to article {article_id}: {result.error_message}")

            return result

        except Exception as e:
            logger.error(f"❌ Error adding reaction to article {article_id}: {e}")
            return ReactionResult(
                success=False,
                article_id=article_id,
                reaction_type=reaction_type,
                error_message=str(e)
            )

    async def remove_article_reaction(
        self,
        access_token: str,
        article_id: str
    ) -> ReactionResult:
        """
        Remove reaction from article.

        Args:
            access_token: CMoney access token
            article_id: Article ID

        Returns:
            ReactionResult
        """
        try:
            result = await self.cmoney_client.remove_article_reaction(
                access_token=access_token,
                article_id=article_id
            )

            if result.success:
                logger.debug(f"✅ Reaction removed from article {article_id}")
            else:
                logger.warning(f"⚠️ Failed to remove reaction from article {article_id}: {result.error_message}")

            return result

        except Exception as e:
            logger.error(f"❌ Error removing reaction from article {article_id}: {e}")
            return ReactionResult(
                success=False,
                article_id=article_id,
                error_message=str(e)
            )

    def clear_token_cache(self, kol_serial: Optional[int] = None):
        """
        Clear token cache.

        Args:
            kol_serial: If provided, clear only this KOL's token. Otherwise clear all.
        """
        if kol_serial:
            if kol_serial in self._token_cache:
                del self._token_cache[kol_serial]
                logger.info(f"🗑️ Cleared token cache for KOL {kol_serial}")
        else:
            self._token_cache.clear()
            logger.info(f"🗑️ Cleared all token cache ({len(self._token_cache)} tokens)")

    def close(self):
        """Close CMoney client."""
        self.cmoney_client.close()
        logger.info("👋 CMoneyReactionClient closed")


# Standalone function for testing
async def test_reaction_client():
    """Test reaction client"""
    import os
    from dotenv import load_dotenv

    load_dotenv()

    client = CMoneyReactionClient()

    print("=" * 60)
    print("CMoney Reaction Client - Test")
    print("=" * 60)

    # Test login (requires real credentials)
    test_email = os.getenv("CMONEY_TEST_EMAIL")
    test_password = os.getenv("CMONEY_TEST_PASSWORD")

    if test_email and test_password:
        print(f"\n🔐 Testing login with {test_email}...")
        token = await client.get_or_refresh_token(
            kol_serial=999,
            email=test_email,
            password=test_password
        )

        if token:
            print(f"✅ Login successful! Token: {token[:20]}...")

            # Test reaction (requires valid article ID)
            test_article_id = os.getenv("CMONEY_TEST_ARTICLE_ID", "12345")
            print(f"\n👍 Testing reaction on article {test_article_id}...")

            result = await client.add_article_reaction(
                access_token=token,
                article_id=test_article_id,
                reaction_type=1
            )

            if result.success:
                print(f"✅ Reaction added successfully!")
            else:
                print(f"❌ Reaction failed: {result.error_message}")
        else:
            print("❌ Login failed")
    else:
        print("⚠️ No test credentials provided (set CMONEY_TEST_EMAIL and CMONEY_TEST_PASSWORD)")

    print("=" * 60)

    client.close()


if __name__ == "__main__":
    import asyncio
    import sys

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    asyncio.run(test_reaction_client())
