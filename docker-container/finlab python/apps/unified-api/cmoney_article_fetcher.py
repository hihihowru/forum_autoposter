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


def fetch_past_hour_articles(hours: int = 1, article_type: str = 'normal') -> List[int]:
    """
    從 Kafka 事件流抓取過去 N 小時的新文章 ID（即時資料）

    Args:
        hours: 回推小時數（預設 1）
        article_type: 文章類型（預設 'normal'）

    Returns:
        List of article IDs (int)
    """
    # 計算時間範圍
    now = datetime.now()
    start_time = now - timedelta(hours=hours)

    # 格式化時間（精確到小時）
    start_datetime = start_time.strftime('%Y-%m-%d %H:00')
    end_datetime = now.strftime('%Y-%m-%d %H:00')

    # 構建 SQL 查詢（基於 Kafka 事件流）
    query = f"""
    with create_post as (
        select
            date_format(timestamp_millis(CAST(CreateTime AS BIGINT)),'yyyy-MM-dd') as ddate,
            date_format(timestamp_millis(CAST(CreateTime AS BIGINT)),'yyyy-MM-dd HH:mm:ss.SSS') as create_time,
            ArticleId as articleid,
            case
                when Content.askPoint > 0 then 'question'
                when Content.groupId > 0 then 'group'
                when Content.newsId > 0 then 'news'
                when Content.botId > 0 then 'bot'
                when Content.creatorId = 4426063 then 'report'
                else Content.articleType
            end as articletype,
            coalesce(Content.creatorId, User.Subject.memberId) as memberid,
            coalesce(Content.appId, User.Subject.appId, get_json_object(User.Application, '$.appId')) as appid
        from ext_create_article_message
        where Content.articleType = '{article_type}'
            and kafka_event_date between to_date('{start_datetime}') and to_date('{end_datetime}')
            and (date_format(timestamp_millis(CAST(CreateTime AS BIGINT)),'yyyy-MM-dd HH:00') >= '{start_datetime}'
                 and date_format(timestamp_millis(CAST(CreateTime AS BIGINT)),'yyyy-MM-dd HH:00') < '{end_datetime}')
    )

    select DISTINCT create_action.articleid, create_action.create_time
    from create_post as create_action
    left join (
        select
            ArticleId as articleid,
            OriginalValue.content.creatorId as memberid,
            to_date(kafka_event_date) as delete_date
        from ext_delete_article_message_struct
        where kafka_event_date between to_date('{start_datetime}') and to_date('{end_datetime}')
    ) as delete_action
        on create_action.articleid = delete_action.articleid
        and create_action.memberid = delete_action.memberid
    where delete_action.delete_date is null
    order by create_action.create_time DESC
    """

    logger.info(f"🔍 [Fetch Articles] Querying Kafka events from {start_datetime} to {end_datetime} (past {hours} hours)")

    status_code, df = query_cmoney_db(query)

    if status_code == 200 and not df.empty:
        # 轉換為整數列表
        article_ids = df['articleid'].astype(int).tolist()
        logger.info(f"✅ [Fetch Articles] Found {len(article_ids)} new articles from Kafka stream")
        return article_ids
    else:
        logger.warning(f"⚠️  [Fetch Articles] No articles found or query failed")
        return []


def test_query():
    """測試查詢功能"""
    try:
        # 先檢查資料表結構（前 5 筆的所有欄位）
        query_structure = """
        SELECT *
        FROM trans_post_latest_all
        LIMIT 5
        """
        status_code, structure_data = query_cmoney_db(query_structure)
        print(f"=== Table Structure (first 5 rows, all columns) ===")
        print(f"Columns: {structure_data.columns.tolist()}")
        print(structure_data.head())

        # 測試查詢（limit 10 筆）
        query = """
        SELECT articleid, createtime, title
        FROM trans_post_latest_all
        LIMIT 10
        """
        status_code, data = query_cmoney_db(query)
        print(f"\nStatus Code: {status_code}")
        print(f"Data:\n{data}")

        # 查詢最新的文章時間
        query_latest = """
        SELECT articleid, createtime, title
        FROM trans_post_latest_all
        WHERE createtime IS NOT NULL
        ORDER BY createtime DESC
        LIMIT 20
        """
        status_code, latest_data = query_cmoney_db(query_latest)
        print(f"\n=== Latest 20 Articles (by createtime) ===")
        print(latest_data)

        # 檢查最新文章的時間是否是今天
        if not latest_data.empty:
            latest_time = pd.to_datetime(latest_data.iloc[0]['createtime'])
            print(f"\n最新文章時間 (createtime): {latest_time}")
            print(f"現在時間: {datetime.now()}")
            time_diff = datetime.now() - latest_time
            print(f"時間差: {time_diff}")

        # 查詢按 ddate 排序的最新文章
        query_ddate = """
        SELECT articleid, createtime, ddate, title
        FROM trans_post_latest_all
        WHERE ddate IS NOT NULL
        ORDER BY ddate DESC
        LIMIT 10
        """
        status_code, ddate_data = query_cmoney_db(query_ddate)
        print(f"\n=== Latest 10 Articles (by ddate) ===")
        print(ddate_data)

        # 測試過去一小時文章（使用新的 Kafka 資料流）
        print(f"\n{'='*60}")
        print(f"Testing Kafka Stream (Real-time Data)")
        print(f"{'='*60}")

        article_ids = fetch_past_hour_articles(hours=1)
        print(f"\n✅ Past 1 hour articles (Kafka): {article_ids[:10] if len(article_ids) > 10 else article_ids}")
        print(f"Total count: {len(article_ids)}")

        # 測試過去 3 小時文章
        article_ids_3h = fetch_past_hour_articles(hours=3)
        print(f"\n✅ Past 3 hours articles (Kafka): {article_ids_3h[:10] if len(article_ids_3h) > 10 else article_ids_3h}")
        print(f"Total count: {len(article_ids_3h)}")

        # 測試過去 24 小時
        now = datetime.now()
        one_day_ago = now - timedelta(hours=24)
        time_filter = one_day_ago.strftime('%Y-%m-%d %H:%M:%S')

        query_24h = f"""
        SELECT COUNT(DISTINCT articleid) as count
        FROM trans_post_latest_all
        WHERE createtime >= '{time_filter}'
        AND articleid IS NOT NULL
        """
        status_code, count_data = query_cmoney_db(query_24h)
        print(f"\nPast 24 hours article count: {count_data}")

    except Exception as err_msg:
        print(f"Error: {str(err_msg)}")


if __name__ == "__main__":
    # 設定 logging
    logging.basicConfig(level=logging.INFO)
    test_query()
