"""
CMoney Real-time Stock Price Service
Fetches 1-minute candlestick data for real-time stock prices
Adapted from ai_chatbot project for forum_autoposter integration
"""

import httpx
import os
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from urllib.parse import quote
import jwt
from zoneinfo import ZoneInfo
import logging

logger = logging.getLogger(__name__)


class CMoneyRealtimeService:
    """Service for fetching real-time stock price data from CMoney API"""

    def __init__(self, email: Optional[str] = None, password: Optional[str] = None):
        # 🔥 Use FORUM_200 credentials (already set in Railway)
        self.email = email or os.getenv("FORUM_200_EMAIL")
        self.password = password or os.getenv("FORUM_200_PASSWORD")
        self.bearer_token = None
        self.user_guid = None
        self.token_expires_at = None
        self.app_id = 2

        # URLs from working client
        self.login_url = "https://social.cmoney.tw/identity/token"
        self.base_url = "https://api.cmoney.tw/AdditionInformationRevisit"

    async def login(self) -> bool:
        """Login and get Bearer token"""

        if not self.email or not self.password:
            logger.error("❌ CMoney credentials not set (FORUM_200_EMAIL, FORUM_200_PASSWORD)")
            return False

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        # Form data (NOT JSON!)
        data = {
            "grant_type": "password",
            "login_method": "email",
            "client_id": "cmstockcommunity",
            "account": self.email,
            "password": self.password
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.login_url,
                    headers=headers,
                    data=data,
                    timeout=10.0
                )

                if response.status_code != 200:
                    logger.error(f"❌ CMoney login failed: {response.status_code}")
                    return False

                result = response.json()
                self.bearer_token = result.get("access_token")
                expires_in = result.get("expires_in", 3600)

                if not self.bearer_token:
                    logger.error(f"❌ No access_token in CMoney response")
                    return False

                # Decode JWT to get user GUID
                try:
                    decoded = jwt.decode(self.bearer_token, options={"verify_signature": False})
                    self.user_guid = decoded.get("user_guid")
                except Exception as e:
                    logger.warning(f"⚠️  Could not decode CMoney JWT: {e}")

                # Use Taiwan timezone for token expiration
                taiwan_tz = ZoneInfo("Asia/Taipei")
                self.token_expires_at = datetime.now(taiwan_tz) + timedelta(seconds=expires_in - 300)

                logger.info(f"✅ CMoney login successful (user: {self.user_guid})")
                return True

        except Exception as e:
            logger.error(f"❌ CMoney login error: {e}")
            return False

    async def ensure_authenticated(self) -> bool:
        """Ensure we have a valid token, login if needed"""

        if self.bearer_token and self.token_expires_at:
            # Use Taiwan timezone for comparison
            taiwan_tz = ZoneInfo("Asia/Taipei")
            if datetime.now(taiwan_tz) < self.token_expires_at:
                return True

        # Token expired or doesn't exist, login
        return await self.login()

    async def get_historical_candlestick(
        self,
        stock_code: str,
        date: Optional[int] = None,
        auto_fallback: bool = True
    ) -> Optional[List[List[Any]]]:
        """
        Get historical 1-minute candlestick data

        Args:
            stock_code: Stock code (e.g., "2330")
            date: Date in YYYYMMDD format (default: today)
            auto_fallback: If True, automatically try previous days if no data

        Returns:
            List of candlestick data arrays or None if failed

        Data format (array indices):
            [0] 索引
            [1] 標的 (stock code)
            [2] 時間間隔
            [3] 開盤價 (open)
            [4] 最高價 (high)
            [5] 最低價 (low)
            [6] 區間成交總量
            [7] 收盤價 (close/current price)
            [8] 累積成交總量 (volume)
            [9] 時間 (timestamp)
            [10] 區間成交總額
            [11] 累計成交總額
        """

        if not await self.ensure_authenticated():
            return None

        taiwan_tz = ZoneInfo("Asia/Taipei")

        if date is None:
            # Use Taiwan timezone for date
            date = int(datetime.now(taiwan_tz).strftime("%Y%m%d"))

        # Build URL
        route = "GetOtherQuery"
        request_type = "HistoryCandlestickKey"
        response_type = "IEnumerable<HistoryCandlestickChart>"
        columns = "索引,標的,時間間隔,開盤價,最高價,最低價,區間成交總量,收盤價,累積成交總量,時間,區間成交總額,累計成交總額"

        encoded_response_type = quote(response_type, safe='')
        url = f"{self.base_url}/api/{route}/{request_type}/{encoded_response_type}?columns={columns}"

        # Request body with AppId and Guid
        payload = {
            "AppId": self.app_id,
            "Guid": self.user_guid,
            "json": json.dumps({"CommKey": stock_code, "Date": date}, ensure_ascii=False)
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.bearer_token}"
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=payload, timeout=30.0)

                if response.status_code == 200:
                    data = response.json()

                    # If data is valid and not empty, return it
                    if data and len(data) > 0:
                        date_str = str(date)
                        formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
                        logger.info(f"✅ CMoney: Got {len(data)} candlestick data points for {stock_code} (date: {formatted_date})")
                        return data

                    # If empty and auto_fallback enabled, try previous days
                    if auto_fallback:
                        logger.warning(f"⚠️  CMoney: No data for {stock_code} on {date}, trying previous days...")

                        # Try up to 5 previous days (handles weekends and holidays)
                        current_date = datetime.strptime(str(date), "%Y%m%d")
                        for days_back in range(1, 6):
                            prev_date = current_date - timedelta(days=days_back)
                            prev_date_int = int(prev_date.strftime("%Y%m%d"))

                            # Recursive call with auto_fallback=False to avoid infinite loop
                            prev_data = await self.get_historical_candlestick(
                                stock_code,
                                date=prev_date_int,
                                auto_fallback=False
                            )

                            if prev_data and len(prev_data) > 0:
                                formatted_prev_date = prev_date.strftime("%Y-%m-%d")
                                logger.info(f"✅ CMoney: Fallback success! Using data from {formatted_prev_date}")
                                return prev_data

                        logger.error(f"❌ CMoney: No data found for {stock_code} in last 5 days")
                        return None

                    return None
                else:
                    logger.error(f"❌ CMoney API error: {response.status_code}")
                    return None

        except Exception as e:
            logger.error(f"❌ CMoney request failed: {e}")
            return None

    async def get_previous_close(
        self,
        stock_code: str,
        date: Optional[int] = None
    ) -> Optional[float]:
        """
        Get previous trading day's close price

        Args:
            stock_code: Stock code
            date: Current date in YYYYMMDD format (will fetch previous day)

        Returns:
            Previous close price or None if unavailable
        """

        if date is None:
            taiwan_tz = ZoneInfo("Asia/Taipei")
            current_date = datetime.now(taiwan_tz)
        else:
            current_date = datetime.strptime(str(date), "%Y%m%d")

        # Try 1 day ago first
        previous_date = current_date - timedelta(days=1)
        previous_date_int = int(previous_date.strftime("%Y%m%d"))
        prev_data = await self.get_historical_candlestick(stock_code, previous_date_int, auto_fallback=False)

        if prev_data and len(prev_data) > 0:
            return float(prev_data[-1][7])

        # If weekend/holiday, try 2 days ago
        previous_date = current_date - timedelta(days=2)
        previous_date_int = int(previous_date.strftime("%Y%m%d"))
        prev_data = await self.get_historical_candlestick(stock_code, previous_date_int, auto_fallback=False)

        if prev_data and len(prev_data) > 0:
            return float(prev_data[-1][7])

        # If still no data, try 3 days ago (long weekend)
        previous_date = current_date - timedelta(days=3)
        previous_date_int = int(previous_date.strftime("%Y%m%d"))
        prev_data = await self.get_historical_candlestick(stock_code, previous_date_int, auto_fallback=False)

        if prev_data and len(prev_data) > 0:
            return float(prev_data[-1][7])

        return None

    def get_price_summary(
        self,
        candlestick_data: List[List[Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        Extract price summary from candlestick data

        Args:
            candlestick_data: Raw candlestick data from API

        Returns:
            Dict with current_price, change, change_pct, high, low, volume, timestamp
        """

        if not candlestick_data or len(candlestick_data) == 0:
            return None

        # Get latest data point (last minute)
        latest = candlestick_data[-1]

        # Extract key metrics
        current_price = float(latest[7])  # 收盤價
        open_price = float(candlestick_data[0][3])  # 開盤價 (first candle)
        high_price = max([float(candle[4]) for candle in candlestick_data])  # 最高價
        low_price = min([float(candle[5]) for candle in candlestick_data])  # 最低價
        volume = int(latest[8])  # 累積成交總量 (張)

        # Extract timestamp
        taiwan_tz = ZoneInfo("Asia/Taipei")
        try:
            timestamp_str = str(latest[9])
            # Try parsing as datetime string first
            if '-' in timestamp_str:
                data_datetime = datetime.strptime(timestamp_str.split('.')[0], "%Y-%m-%d %H:%M:%S")
                data_datetime = data_datetime.replace(tzinfo=taiwan_tz)
            else:
                # Try parsing as epoch milliseconds
                timestamp_ms = int(timestamp_str)
                data_datetime = datetime.fromtimestamp(timestamp_ms / 1000, tz=taiwan_tz)
        except:
            # Fallback to current time if parsing fails
            data_datetime = datetime.now(taiwan_tz)

        # Calculate price change (vs open for now, will be updated with previous close)
        price_change = current_price - open_price
        price_change_pct = (price_change / open_price * 100) if open_price > 0 else 0

        return {
            "current_price": round(current_price, 2),
            "open_price": round(open_price, 2),
            "high_price": round(high_price, 2),
            "low_price": round(low_price, 2),
            "volume": volume,
            "price_change": round(price_change, 2),
            "price_change_pct": round(price_change_pct, 2),
            "timestamp": data_datetime.strftime("%Y-%m-%d %H:%M:%S"),
            "is_realtime": True
        }

    async def get_realtime_stock_price(
        self,
        stock_code: str,
        stock_name: str
    ) -> Dict[str, Any]:
        """
        Get real-time stock price with full details
        This is the main method to be called by content generation

        Args:
            stock_code: Stock code (e.g., "2330")
            stock_name: Stock name (e.g., "台積電")

        Returns:
            Dict with price data including:
            - current_price, open_price, high_price, low_price
            - volume, price_change, price_change_pct
            - timestamp, previous_close
            - formatted_text (for AI prompt)
        """

        try:
            # Fetch candlestick data
            candlestick_data = await self.get_historical_candlestick(stock_code)

            if not candlestick_data or len(candlestick_data) == 0:
                logger.warning(f"⚠️  No candlestick data for {stock_code}, returning placeholder")
                return {
                    "stock_code": stock_code,
                    "stock_name": stock_name,
                    "error": "無即時價格資料",
                    "is_realtime": False
                }

            # Extract price summary
            price_summary = self.get_price_summary(candlestick_data)

            if not price_summary:
                return {
                    "stock_code": stock_code,
                    "stock_name": stock_name,
                    "error": "無法解析價格資料",
                    "is_realtime": False
                }

            # Get previous close for accurate day-over-day calculation
            previous_close = await self.get_previous_close(stock_code)

            # Recalculate price change with previous close
            if previous_close:
                current_price = price_summary["current_price"]
                price_change = current_price - previous_close
                price_change_pct = (price_change / previous_close * 100) if previous_close > 0 else 0
                price_summary["price_change"] = round(price_change, 2)
                price_summary["price_change_pct"] = round(price_change_pct, 2)
                price_summary["previous_close"] = round(previous_close, 2)

            # Add stock identifiers
            price_summary["stock_code"] = stock_code
            price_summary["stock_name"] = stock_name

            # Format text for AI prompt
            change_str = f"{price_summary['price_change']:+.2f} ({price_summary['price_change_pct']:+.2f}%)"
            formatted_text = f"""## 即時股價資訊（{price_summary['timestamp']}）

**{stock_name}（{stock_code}）**
- 當前股價：{price_summary['current_price']} 元
- 漲跌幅：{change_str}
- 今日開盤：{price_summary['open_price']} 元
- 今日最高：{price_summary['high_price']} 元
- 今日最低：{price_summary['low_price']} 元
- 成交量：{price_summary['volume']:,} 張
"""

            if previous_close:
                formatted_text += f"- 昨日收盤：{price_summary['previous_close']} 元\n"

            price_summary["formatted_text"] = formatted_text

            logger.info(f"✅ Successfully fetched real-time price for {stock_name}({stock_code}): {price_summary['current_price']} ({change_str})")

            return price_summary

        except Exception as e:
            logger.error(f"❌ Error fetching real-time price for {stock_code}: {e}")
            return {
                "stock_code": stock_code,
                "stock_name": stock_name,
                "error": str(e),
                "is_realtime": False
            }


# Singleton instance
_cmoney_service: Optional[CMoneyRealtimeService] = None


def get_cmoney_service() -> CMoneyRealtimeService:
    """Get or create singleton CMoney service instance"""
    global _cmoney_service
    if _cmoney_service is None:
        _cmoney_service = CMoneyRealtimeService()
    return _cmoney_service
