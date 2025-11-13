# -*- coding: utf-8 -*-
"""
CMoney Article Fetcher
從 CMoney 資料庫抓取文章資料
"""

import pandas as pd
import random
import requests
import json
from datetime import datetime, timedelta
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)

# CMoney API Cookie (from your provided code)
CMONEY_COOKIE = 'PLAY_SESSION=eyJhbGciOiJIUzI1NiJ9.eyJkYXRhIjp7InVzZXJuYW1lIjoiZm9ydW10ZWFtIn0sIm5iZiI6MTc2MjgzOTI1OCwiaWF0IjoxNzYyODM5MjU4fQ.2KV6UwSaNLjvdYjLCppy1BJ84hgpMKb1qhLJ_2tpmKg'


def query_cmoney_db(sql_query: str) -> Tuple[int, pd.DataFrame]:
    """
    查詢 CMoney 資料庫

    Args:
        sql_query: SQL 查詢語句

    Returns:
        (status_code, dataframe)
    """
    job_id = random.randrange(10000000, 99999999, 1)
    logger.info(f"🔍 [CMoney Query] jobid: {job_id}")

    url = 'https://anya.cmoney.tw/api/queryResult'

    headers = {
        'Cookie': CMONEY_COOKIE,
        'Content-Type': 'application/json; charset=UTF-8',
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive'
    }

    body = {
        'jobId': job_id,
        'limit': 99999999,
        'sql': sql_query,
        'txDate': '2023-03-28 00:00:00'
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(body), timeout=30)
        status_code = response.status_code

        logger.info(f"✅ [CMoney Query] status_code: {status_code}")

        if status_code == 200:
            json_data = response.content.decode('utf-8')
            df_dict = json.loads(json_data)
            df = pd.DataFrame(df_dict['data'], columns=df_dict['columns'])
            logger.info(f"✅ [CMoney Query] Retrieved {len(df)} rows")
            return status_code, df
        else:
            logger.error(f"❌ [CMoney Query] Failed with status {status_code}")
            return status_code, pd.DataFrame()

    except Exception as e:
        logger.error(f"❌ [CMoney Query] Error: {e}")
        return 500, pd.DataFrame()


def fetch_past_hour_articles() -> List[int]:
    """
    抓取過去一小時的新文章 ID

    Returns:
        List of article IDs (int)
    """
    # 計算時間範圍（過去一小時）
    now = datetime.now()
    one_hour_ago = now - timedelta(hours=1)

    # 格式化時間為字串（根據 createtime 欄位格式調整）
    time_filter = one_hour_ago.strftime('%Y-%m-%d %H:%M:%S')

    # 構建 SQL 查詢
    query = f"""
    SELECT DISTINCT articleid
    FROM trans_post_latest_all
    WHERE createtime >= '{time_filter}'
    AND articleid IS NOT NULL
    ORDER BY createtime DESC
    """

    logger.info(f"🔍 [Fetch Articles] Querying articles since {time_filter}")

    status_code, df = query_cmoney_db(query)

    if status_code == 200 and not df.empty:
        # 轉換為整數列表
        article_ids = df['articleid'].astype(int).tolist()
        logger.info(f"✅ [Fetch Articles] Found {len(article_ids)} new articles")
        return article_ids
    else:
        logger.warning(f"⚠️  [Fetch Articles] No articles found or query failed")
        return []


def test_query():
    """測試查詢功能"""
    try:
        # 測試查詢（limit 10 筆）
        query = """
        SELECT articleid, createtime, title
        FROM trans_post_latest_all
        LIMIT 10
        """
        status_code, data = query_cmoney_db(query)
        print(f"Status Code: {status_code}")
        print(f"Data:\n{data}")

        # 測試過去一小時文章
        article_ids = fetch_past_hour_articles()
        print(f"\nPast hour articles: {article_ids}")

    except Exception as err_msg:
        print(f"Error: {str(err_msg)}")


if __name__ == "__main__":
    # 設定 logging
    logging.basicConfig(level=logging.INFO)
    test_query()
