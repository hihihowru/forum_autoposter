"""
DTNO Service - Fetch stock data from CMoney DTNO tables
Based on the 3-level hierarchy: Category > SubCategory > Columns
"""

import httpx
from typing import Optional, Dict, Any, List
from datetime import datetime
from .cmoney_realtime import get_cmoney_service
import logging

logger = logging.getLogger(__name__)


# ============================================
# DTNO Table Mapping (SubCategory -> Table ID)
# ============================================

DTNO_TABLE_MAPPING = {
    # ========== 基本面 (9張) ==========
    'revenue_stats': '115694276',     # 月營收統計 (創新高、連續成長)
    'revenue': '115694491',           # 月營收詳細 (營收金額、年增率)
    'eps': '115694323',               # 財報摘要 (EPS、毛利率、營益率)
    'profitability': '115694323',     # 獲利能力 (same table as eps)
    'eps_estimate': '115694449',      # 機構預估EPS (預估EPS、目標價)
    'quarterly_earnings': '115694772', # 季盈餘公司自結
    'financial_health': '115694602',  # IFRS年財報 (負債比、ROE)
    'dividend': '115394894',          # 股利與股票
    'analyst_rating': '115694873',    # 個股機構績效評等

    # ========== 技術面 (8張) ==========
    'daily_close': '115695215',       # 日收盤表 (OHLCV)
    'prediction': '115694668',        # 預測主要股
    'daily_kline': '115694759',       # 主要股日K線
    'ma': '115694997',                # 常用技術指標_均線
    'momentum': '115695101',          # 日乖離比較表 (報酬率)
    'yearly_stats': '115695150',      # 個股年份統計表
    'technical': '115695868',         # 技術指標1 (KD、RSI、MACD、乖離率、波動率)
    'industry': '113775643',          # 產業標的
    # 技術面別名 (向後相容)
    'kd': '115695868',                # alias → technical
    'rsi': '115695868',               # alias → technical
    'macd': '115695868',              # alias → technical
    'bias': '115695868',              # alias → technical
    'volatility': '115695868',        # alias → technical

    # ========== 籌碼面 (14張) ==========
    'institutional': '115696346',     # 三大主力 (外資、投信、自營商合計)
    'foreign_detail': '115696245',    # 外資詳細
    'trust_detail': '115696307',      # 投信詳細
    'dealer_detail': '115696320',     # 自營商詳細
    'broker_top1': '115085458',       # top1券商統計 (籌碼集中度)
    'broker_top5': '115085822',       # top5券商統計
    'broker_top10': '115085871',      # top10券商統計
    'broker_top15': '115085886',      # top15券商統計
    'broker_daily_top15': '115085927', # 每日top15券商統計
    'winner_loser': '115085952',      # 個股贏家統計
    'major_select': '115696523',      # 分點主力選股
    'major_daily': '115696587',       # 日主力買超出表
    'major_trading': '115696668',     # 個股主力買超統計
    'broker_analysis': '115696306',   # 分點籌碼分析
    # 籌碼面別名 (向後相容)
    'concentration': '115085458',     # alias → broker_top1
    'broker': '115696587',            # alias → major_daily
    'major_streak': '115696523',      # alias → major_select
}

# Period type for each table (day/month/quarter)
DTNO_PERIOD_TYPE = {
    # 基本面
    'revenue_stats': 'month',
    'revenue': 'month',
    'eps': 'quarter',
    'profitability': 'quarter',
    'eps_estimate': 'month',
    'quarterly_earnings': 'quarter',
    'financial_health': 'quarter',
    'dividend': 'year',
    'analyst_rating': 'day',
    # 技術面
    'daily_close': 'day',
    'prediction': 'day',
    'daily_kline': 'day',
    'ma': 'day',
    'momentum': 'day',
    'yearly_stats': 'year',
    'technical': 'day',
    'industry': 'day',
    'kd': 'day',           # alias
    'rsi': 'day',          # alias
    'macd': 'day',         # alias
    'bias': 'day',         # alias
    'volatility': 'day',   # alias
    # 籌碼面
    'institutional': 'day',
    'foreign_detail': 'day',
    'trust_detail': 'day',
    'dealer_detail': 'day',
    'broker_top1': 'day',
    'broker_top5': 'day',
    'broker_top10': 'day',
    'broker_top15': 'day',
    'broker_daily_top15': 'day',
    'winner_loser': 'day',
    'major_select': 'day',
    'major_daily': 'day',
    'major_trading': 'day',
    'broker_analysis': 'day',
    'concentration': 'day',  # alias
    'broker': 'day',         # alias
    'major_streak': 'day',   # alias
}


class DTNOService:
    """Service for fetching DTNO data tables"""

    def __init__(self):
        self.cmoney = get_cmoney_service()
        self.dtno_url = "https://outpost.cmoney.tw/MobileService/ashx/GetDtnoData.ashx"

    async def _fetch_dtno_table(
        self,
        dtno_id: str,
        stock_code: str,
        dt_range: int = 10
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch data from a DTNO table

        Args:
            dtno_id: DTNO table ID
            stock_code: Stock code (e.g., "2330")
            dt_range: Number of periods to fetch

        Returns:
            Dict with 'Title' (column names) and 'Data' (rows), or None if failed
        """
        if not await self.cmoney.ensure_authenticated():
            logger.error("CMoney authentication failed")
            return None

        payload = {
            "action": "getdtnodata",
            "AppId": "99",
            "DtNo": dtno_id,
            "ParamStr": f"AssignID={stock_code};DTRange={dt_range}",
            "AssignSPID": "",
            "KeyMap": "",
            "FilterNo": "0"
        }

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Bearer {self.cmoney.bearer_token}"
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.dtno_url,
                    headers=headers,
                    data=payload,
                    timeout=30.0
                )

                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"DTNO fetch success: table={dtno_id}, stock={stock_code}")
                    return data
                else:
                    logger.error(f"DTNO API error ({dtno_id}): {response.status_code}")
                    return None

        except Exception as e:
            logger.error(f"DTNO request failed ({dtno_id}): {e}")
            return None

    async def fetch_by_subcategories(
        self,
        stock_code: str,
        sub_categories: List[str]
    ) -> Dict[str, Any]:
        """
        Fetch data for selected subcategories

        Args:
            stock_code: Stock code (e.g., "2330")
            sub_categories: List of subcategory IDs (e.g., ['revenue', 'ma', 'institutional'])

        Returns:
            Dict with subcategory as key and data as value
        """
        results = {}

        # Dedupe table IDs to avoid redundant fetches
        table_to_subcats: Dict[str, List[str]] = {}
        for sub_cat in sub_categories:
            table_id = DTNO_TABLE_MAPPING.get(sub_cat)
            if table_id:
                if table_id not in table_to_subcats:
                    table_to_subcats[table_id] = []
                table_to_subcats[table_id].append(sub_cat)

        # Fetch each unique table
        for table_id, subcats in table_to_subcats.items():
            # Determine period based on first subcat
            period_type = DTNO_PERIOD_TYPE.get(subcats[0], 'day')

            if period_type == 'day':
                dt_range = 20  # Last 20 days
            elif period_type == 'month':
                dt_range = 12  # Last 12 months
            elif period_type == 'quarter':
                dt_range = 8   # Last 8 quarters
            else:
                dt_range = 5   # Default

            data = await self._fetch_dtno_table(table_id, stock_code, dt_range)

            if data:
                # Store under each subcategory that uses this table
                for sub_cat in subcats:
                    results[sub_cat] = {
                        'table_id': table_id,
                        'titles': data.get('Title', []),
                        'data': data.get('Data', []),
                        'row_count': len(data.get('Data', []))
                    }
                    logger.info(f"Fetched {sub_cat}: {results[sub_cat]['row_count']} rows")

        return results

    def format_for_prompt(
        self,
        stock_code: str,
        stock_name: str,
        dtno_data: Dict[str, Any]
    ) -> str:
        """
        Format DTNO data into a prompt-friendly string

        Args:
            stock_code: Stock code
            stock_name: Stock name
            dtno_data: Result from fetch_by_subcategories()

        Returns:
            Formatted string for GPT prompt injection
        """
        if not dtno_data:
            return ""

        lines = [f"\n## {stock_name}（{stock_code}）數據分析資料\n"]

        for sub_cat, data in dtno_data.items():
            if not data or not data.get('data'):
                continue

            titles = data.get('titles', [])
            rows = data.get('data', [])

            # Get subcategory display name
            sub_cat_names = {
                'revenue': '營收統計',
                'eps': 'EPS與盈餘',
                'profitability': '獲利能力',
                'financial_health': '財務健康',
                'dividend': '股利政策',
                'analyst_rating': '機構評等',
                'momentum': '價格動能',
                'ma': '均線系統',
                'kd': 'KD指標',
                'rsi': 'RSI指標',
                'macd': 'MACD指標',
                'bias': '乖離率',
                'volatility': '波動率',
                'institutional': '三大法人',
                'foreign_detail': '外資詳細',
                'trust_detail': '投信詳細',
                'concentration': '籌碼集中度',
                'major_trading': '主力買賣超',
                'broker': '券商分點',
                'major_streak': '主力連續買賣',
                'winner_loser': '贏家/輸家統計',
            }

            display_name = sub_cat_names.get(sub_cat, sub_cat)
            lines.append(f"\n### {display_name}\n")

            # Take only latest row for summary
            if rows:
                latest_row = rows[0]

                # Format key columns (skip first few meta columns)
                for i, title in enumerate(titles):
                    if i < 4:  # Skip date, time, code, name columns
                        continue
                    if i >= len(latest_row):
                        break

                    value = latest_row[i]
                    if value is not None and value != '':
                        # Format numeric values
                        try:
                            num_val = float(value)

                            # 🔥 FIX: Handle unit conversion based on column title
                            # DTNO data uses (千) for thousands, (百萬) for millions
                            display_title = title
                            if '(千)' in title or '（千）' in title or '(千元)' in title or '（千元）' in title:
                                num_val = num_val * 1000  # Convert 千/千元 to actual value
                                display_title = title.replace('(千)', '').replace('（千）', '').replace('(千元)', '').replace('（千元）', '').strip()
                            elif '(百萬)' in title or '（百萬）' in title:
                                num_val = num_val * 1000000  # Convert 百萬 to actual value
                                display_title = title.replace('(百萬)', '').replace('（百萬）', '').strip()

                            # 🔥 FIX: Use Chinese units (萬、億) instead of K/M
                            if abs(num_val) >= 100000000:  # 1億以上
                                formatted = f"{num_val/100000000:.2f}億"
                            elif abs(num_val) >= 10000:  # 1萬以上
                                formatted = f"{num_val/10000:.2f}萬"
                            elif num_val == int(num_val):  # 整數
                                formatted = f"{int(num_val)}"
                            else:
                                formatted = f"{num_val:.2f}"
                            lines.append(f"- {display_title}: {formatted}")
                        except (ValueError, TypeError):
                            lines.append(f"- {title}: {value}")

        return "\n".join(lines)


    async def get_stock_news(
        self,
        stock_code: str,
        days: int = 3
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Fetch stock news from DTNO (個股新聞 table)

        Args:
            stock_code: Stock code (e.g., "2330")
            days: Number of days to filter (default: 3, only recent news)

        Returns:
            List of news articles with title, content, and datetime, or None if failed
            Example: [
                {
                    'date': '2025-11-12',
                    'datetime': '2025/11/12 01:23:10',
                    'title': '蘋果新品助攻後市看俏...',
                    'content': '外資高盛證券最新報告...',
                    'link': '',  # No link for DTNO news
                    'source': 'CMoney'
                },
                ...
            ]
        """
        from datetime import timedelta

        # DTNO Table ID for stock news
        DTNO_STOCK_NEWS_ID = "105567992"

        if not await self.cmoney.ensure_authenticated():
            logger.error(f"CMoney authentication failed, cannot fetch news for {stock_code}")
            return None

        payload = {
            "action": "getdtnodata",
            "AppId": "99",
            "DtNo": DTNO_STOCK_NEWS_ID,
            "ParamStr": f"AssignID={stock_code};MTPeriod=0;DTMode=0;DTRange=5;DTOrder=1;MajorTable=M173;",
            "AssignSPID": "",
            "KeyMap": "",
            "FilterNo": "0"
        }

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Bearer {self.cmoney.bearer_token}"
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.dtno_url,
                    headers=headers,
                    data=payload
                )

                if response.status_code != 200:
                    logger.error(f"DTNO News API error: {response.status_code}")
                    return None

                data = response.json()

                if 'Title' not in data or 'Data' not in data:
                    logger.warning(f"DTNO News: Invalid response structure for {stock_code}")
                    return None

                rows = data['Data']
                logger.info(f"DTNO News: Got {len(rows)} total news for {stock_code}")

                # Filter news from last N days
                cutoff_date = datetime.now() - timedelta(days=days)
                recent_news = []

                for row in rows:
                    if len(row) < 4:  # Need at least date, datetime, title, content
                        continue

                    # Parse date (format: YYYYMMDD)
                    date_str = str(row[0])
                    try:
                        if len(date_str) == 8 and date_str.isdigit():
                            news_date = datetime.strptime(date_str, '%Y%m%d')
                        else:
                            continue  # Skip invalid dates

                        # Only include news from last N days
                        if news_date >= cutoff_date:
                            recent_news.append({
                                'date': news_date.strftime('%Y-%m-%d'),
                                'datetime': str(row[1]),  # 發布日期時間
                                'title': str(row[2]),  # 新聞標題
                                'snippet': str(row[3])[:200],  # 新聞內容 (truncated for prompt)
                                'content': str(row[3]),  # Full content
                                'link': '',  # DTNO news don't have links
                                'source': 'CMoney'
                            })
                    except Exception as e:
                        # Skip unparseable dates
                        continue

                logger.info(f"DTNO News: Filtered {len(recent_news)} news from last {days} days for {stock_code}")
                return recent_news if len(recent_news) > 0 else None

        except Exception as e:
            logger.error(f"Error fetching DTNO news for {stock_code}: {e}")
            return None


# Singleton instance
_dtno_service: Optional[DTNOService] = None


def get_dtno_service() -> DTNOService:
    """Get or create singleton DTNO service instance"""
    global _dtno_service
    if _dtno_service is None:
        _dtno_service = DTNOService()
    return _dtno_service
