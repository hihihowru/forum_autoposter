"""
Article Stream Fetcher Service
Fetches newly created article IDs every hour from CMoney API

Created: 2025-11-10
Author: Claude Code
"""

import pandas as pd
import random
import requests
import json
import logging
from datetime import datetime, timedelta
from typing import List, Tuple, Optional

logger = logging.getLogger(__name__)


class ArticleStreamFetcher:
    """
    Fetches newly created article IDs from CMoney API.

    This service queries the CMoney database to get articles created
    in the past hour and returns their IDs for reaction bot processing.
    """

    def __init__(self, cookie_session: Optional[str] = None):
        """
        Initialize article stream fetcher.

        Args:
            cookie_session: CMoney API session cookie (optional, reads from env if not provided)
        """
        import os

        # Priority: 1) Parameter, 2) Environment variable, 3) Fallback default
        self.cookie_session = (
            cookie_session or
            os.getenv('CMONEY_ARTICLE_COOKIE') or
            'eyJhbGciOiJIUzI1NiJ9.eyJkYXRhIjp7InVzZXJuYW1lIjoiZm9ydW10ZWFtIn0sIm5iZiI6MTc2MjgzOTI1OCwiaWF0IjoxNzYyODM5MjU4fQ.2KV6UwSaNLjvdYjLCppy1BJ84hgpMKb1qhLJ_2tpmKg'
        )
        self.api_url = 'https://anya.cmoney.tw/api/queryResult'

        # Log which source was used (for debugging)
        if cookie_session:
            logger.info("✅ ArticleStreamFetcher initialized (using provided cookie)")
        elif os.getenv('CMONEY_ARTICLE_COOKIE'):
            logger.info("✅ ArticleStreamFetcher initialized (using env CMONEY_ARTICLE_COOKIE)")
        else:
            logger.warning("⚠️ ArticleStreamFetcher using fallback cookie (may expire!)")

        logger.info("✅ ArticleStreamFetcher initialized")

    def _generate_job_id(self) -> int:
        """Generate random job ID for CMoney API request."""
        return random.randrange(10000000, 99999999, 1)

    def _make_api_request(self, query: str) -> Tuple[int, pd.DataFrame]:
        """
        Make request to CMoney API.

        Args:
            query: SQL query to execute

        Returns:
            Tuple of (status_code, dataframe)
        """
        job_id = self._generate_job_id()
        logger.info(f"📤 Making API request with job_id: {job_id}")

        headers = {
            'Cookie': f'PLAY_SESSION={self.cookie_session}',
            'Content-Type': 'application/json; charset=UTF-8',
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive'
        }

        body = {
            'jobId': job_id,
            'limit': 99999999,
            'sql': query,
            'txDate': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        try:
            response = requests.post(self.api_url, headers=headers, data=json.dumps(body), timeout=30)
            status_code = response.status_code

            logger.info(f"📥 API response status: {status_code}")

            if status_code == 200:
                df_data = json.loads(response.content.decode('utf-8'))

                if 'data' in df_data and 'columns' in df_data:
                    data = pd.DataFrame(df_data['data'], columns=df_data['columns'])
                    logger.info(f"✅ Retrieved {len(data)} rows")
                    return status_code, data
                else:
                    logger.warning(f"⚠️ Unexpected response format: {df_data}")
                    return status_code, pd.DataFrame()
            else:
                logger.error(f"❌ API request failed with status {status_code}")
                return status_code, pd.DataFrame()

        except requests.exceptions.Timeout:
            logger.error("❌ API request timeout")
            return 408, pd.DataFrame()
        except Exception as e:
            logger.error(f"❌ API request error: {e}")
            return 500, pd.DataFrame()

    def fetch_hourly_articles(
        self,
        hours_back: int = 1,
        custom_start_time: Optional[datetime] = None,
        custom_end_time: Optional[datetime] = None
    ) -> Tuple[int, List[str]]:
        """
        Fetch article IDs created in the past N hours.

        Args:
            hours_back: Number of hours to look back (default: 1)
            custom_start_time: Optional custom start time (overrides hours_back)
            custom_end_time: Optional custom end time (overrides current time)

        Returns:
            Tuple of (status_code, list_of_article_ids)
        """
        try:
            # Calculate time range
            if custom_end_time:
                end_time = custom_end_time
            else:
                end_time = datetime.now().replace(minute=0, second=0, microsecond=0)

            if custom_start_time:
                start_time = custom_start_time
            else:
                start_time = (end_time - timedelta(hours=hours_back))

            logger.info(f"🕐 Fetching articles from {start_time} to {end_time}")

            # Build SQL query
            query = f"""
                SELECT article_id
                FROM trans_post_latest_all
                WHERE create_time >= '{start_time.strftime("%Y-%m-%d %H:%M:%S")}'
                  AND create_time < '{end_time.strftime("%Y-%m-%d %H:%M:%S")}'
            """

            # Execute query
            status_code, data = self._make_api_request(query)

            if status_code == 200 and not data.empty:
                # Extract article IDs as list
                article_ids = data['article_id'].astype(str).tolist()

                logger.info(f"✅ Successfully fetched {len(article_ids)} article IDs")
                logger.debug(f"Article IDs sample (first 10): {article_ids[:10]}")

                return status_code, article_ids
            else:
                logger.warning(f"⚠️ No articles found or API error (status: {status_code})")
                return status_code, []

        except Exception as e:
            logger.error(f"❌ Error fetching hourly articles: {e}")
            return 500, []

    def fetch_and_save(
        self,
        output_path: Optional[str] = None,
        hours_back: int = 1
    ) -> Tuple[int, List[str], Optional[str]]:
        """
        Fetch articles and optionally save to CSV.

        Args:
            output_path: Path to save CSV (optional, auto-generated if None)
            hours_back: Number of hours to look back

        Returns:
            Tuple of (status_code, article_ids, csv_path)
        """
        status_code, article_ids = self.fetch_hourly_articles(hours_back=hours_back)

        if status_code == 200 and article_ids:
            # Generate CSV path if not provided
            if not output_path:
                timestamp = datetime.now().strftime('%Y%m%d_%H')
                output_path = f"new_articles_{timestamp}.csv"

            # Save to CSV
            try:
                df = pd.DataFrame({'article_id': article_ids})
                df.to_csv(output_path, index=False)
                logger.info(f"💾 Data saved to {output_path}")
                return status_code, article_ids, output_path
            except Exception as e:
                logger.error(f"❌ Error saving CSV: {e}")
                return status_code, article_ids, None
        else:
            return status_code, article_ids, None

    def fetch_with_details(
        self,
        hours_back: int = 1,
        include_columns: Optional[List[str]] = None
    ) -> Tuple[int, pd.DataFrame]:
        """
        Fetch articles with additional details (not just IDs).

        Args:
            hours_back: Number of hours to look back
            include_columns: Optional list of additional columns to fetch

        Returns:
            Tuple of (status_code, dataframe)
        """
        try:
            end_time = datetime.now().replace(minute=0, second=0, microsecond=0)
            start_time = end_time - timedelta(hours=hours_back)

            # Build column list
            if include_columns:
                columns_str = ', '.join(['article_id'] + include_columns)
            else:
                columns_str = 'article_id, member_id, create_time, topic_id'

            query = f"""
                SELECT {columns_str}
                FROM trans_post_latest_all
                WHERE create_time >= '{start_time.strftime("%Y-%m-%d %H:%M:%S")}'
                  AND create_time < '{end_time.strftime("%Y-%m-%d %H:%M:%S")}'
            """

            status_code, data = self._make_api_request(query)

            return status_code, data

        except Exception as e:
            logger.error(f"❌ Error fetching article details: {e}")
            return 500, pd.DataFrame()


# Standalone function for cron job / script usage
def fetch_hourly_articles_standalone(
    cookie_session: Optional[str] = None,
    save_csv: bool = True,
    hours_back: int = 1
) -> List[str]:
    """
    Standalone function to fetch hourly articles.
    Can be called directly from cron job or scheduled task.

    Args:
        cookie_session: CMoney API session cookie
        save_csv: Whether to save results to CSV
        hours_back: Number of hours to look back

    Returns:
        List of article IDs

    Example:
        >>> article_ids = fetch_hourly_articles_standalone()
        >>> print(f"Found {len(article_ids)} new articles")
    """
    fetcher = ArticleStreamFetcher(cookie_session=cookie_session)

    if save_csv:
        status_code, article_ids, csv_path = fetcher.fetch_and_save(hours_back=hours_back)
        if csv_path:
            print(f"✅ Saved {len(article_ids)} article IDs to {csv_path}")
    else:
        status_code, article_ids = fetcher.fetch_hourly_articles(hours_back=hours_back)

    if status_code == 200:
        print(f"✅ Successfully fetched {len(article_ids)} article IDs")
        return article_ids
    else:
        print(f"❌ Failed to fetch articles (status: {status_code})")
        return []


# Main execution (for testing)
if __name__ == "__main__":
    import sys

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("=" * 60)
    print("Article Stream Fetcher - Test Run")
    print("=" * 60)

    # Parse command line arguments
    hours_back = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    save_csv = sys.argv[2].lower() == 'true' if len(sys.argv) > 2 else True

    # Run fetcher
    article_ids = fetch_hourly_articles_standalone(
        save_csv=save_csv,
        hours_back=hours_back
    )

    print("=" * 60)
    print(f"Total articles found: {len(article_ids)}")
    if article_ids:
        print(f"Sample (first 10): {article_ids[:10]}")
    print("=" * 60)
