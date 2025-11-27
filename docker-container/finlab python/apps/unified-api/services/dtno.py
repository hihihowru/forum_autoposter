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
    # 基本面
    'revenue': '115694491',           # 營收統計
    'eps': '115694323',               # EPS與盈餘
    'profitability': '115694323',     # 獲利能力 (same table as EPS)
    'financial_health': '115694602',  # 財務健康
    'dividend': '115394894',          # 股利政策
    'analyst_rating': '115694873',    # 機構評等

    # 技術面
    'momentum': '115695101',          # 價格動能
    'ma': '115694997',                # 均線系統
    'kd': '115695868',                # KD指標
    'rsi': '115695868',               # RSI指標 (same table)
    'macd': '115695868',              # MACD指標 (same table)
    'bias': '115695868',              # 乖離率 (same table)
    'volatility': '115695868',        # 波動率 (same table)

    # 籌碼面
    'institutional': '115696346',     # 三大法人
    'foreign_detail': '115696245',    # 外資詳細
    'trust_detail': '115696307',      # 投信詳細
    'concentration': '115085458',     # 籌碼集中度
    'major_trading': '115696668',     # 主力買賣超
    'broker': '115696587',            # 券商分點
    'major_streak': '115696523',      # 主力連續買賣
    'winner_loser': '115085952',      # 贏家/輸家統計
}

# Period type for each table (day/month/quarter)
DTNO_PERIOD_TYPE = {
    'revenue': 'month',
    'eps': 'quarter',
    'profitability': 'quarter',
    'financial_health': 'quarter',
    'dividend': 'year',
    'analyst_rating': 'day',
    'momentum': 'day',
    'ma': 'day',
    'kd': 'day',
    'rsi': 'day',
    'macd': 'day',
    'bias': 'day',
    'volatility': 'day',
    'institutional': 'day',
    'foreign_detail': 'day',
    'trust_detail': 'day',
    'concentration': 'day',
    'major_trading': 'day',
    'broker': 'day',
    'major_streak': 'day',
    'winner_loser': 'day',
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
                            if abs(num_val) >= 1000000:
                                formatted = f"{num_val/1000000:.2f}M"
                            elif abs(num_val) >= 1000:
                                formatted = f"{num_val/1000:.2f}K"
                            else:
                                formatted = f"{num_val:.2f}"
                            lines.append(f"- {title}: {formatted}")
                        except (ValueError, TypeError):
                            lines.append(f"- {title}: {value}")

        return "\n".join(lines)


# Singleton instance
_dtno_service: Optional[DTNOService] = None


def get_dtno_service() -> DTNOService:
    """Get or create singleton DTNO service instance"""
    global _dtno_service
    if _dtno_service is None:
        _dtno_service = DTNOService()
    return _dtno_service
