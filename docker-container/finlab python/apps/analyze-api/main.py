from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import numpy as np
from typing import List, Dict, Any

class OHLCItem(BaseModel):
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: float

class AnalyzeIn(BaseModel):
    stock_id: str
    ohlc: List[OHLCItem]

app = FastAPI()

def ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False).mean()

def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = np.where(delta > 0, delta, 0.0)
    loss = np.where(delta < 0, -delta, 0.0)
    gain_series = pd.Series(gain, index=series.index)
    loss_series = pd.Series(loss, index=series.index)
    avg_gain = gain_series.rolling(window=period, min_periods=period).mean()
    avg_loss = loss_series.rolling(window=period, min_periods=period).mean()
    # Wilder smoothing after seed
    avg_gain = avg_gain.combine_first(pd.Series(index=series.index, dtype=float))
    avg_loss = avg_loss.combine_first(pd.Series(index=series.index, dtype=float))
    for i in range(period, len(series)):
        avg_gain.iat[i] = (avg_gain.iat[i-1] * (period - 1) + gain_series.iat[i]) / period
        avg_loss.iat[i] = (avg_loss.iat[i-1] * (period - 1) + loss_series.iat[i]) / period
    rs = avg_gain / (avg_loss.replace(0, np.nan))
    rsi_val = 100 - (100 / (1 + rs))
    return rsi_val.fillna(method='bfill')

def macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    ema_fast = ema(series, fast)
    ema_slow = ema(series, slow)
    macd_line = ema_fast - ema_slow
    signal_line = ema(macd_line, signal)
    hist = macd_line - signal_line
    return macd_line, signal_line, hist

def atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    high_low = (high - low).abs()
    high_close = (high - close.shift(1)).abs()
    low_close = (low - close.shift(1)).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    return tr.rolling(window=period, min_periods=period).mean()

@app.post("/analyze")
def analyze(body: AnalyzeIn):
    df = pd.DataFrame([x.model_dump() for x in body.ohlc])
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)

    # Indicators
    df["MA5"] = df["close"].rolling(window=5).mean()
    df["MA20"] = df["close"].rolling(window=20).mean()
    df["MA60"] = df["close"].rolling(window=60).mean()
    df["RSI14"] = rsi(df["close"], 14)
    macd_line, signal_line, hist = macd(df["close"], 12, 26, 9)
    df["MACD"] = macd_line
    df["MACD_SIGNAL"] = signal_line
    df["MACD_HIST"] = hist
    df["ATR14"] = atr(df["high"], df["low"], df["close"], 14)

    # Signals
    signals: List[Dict[str, Any]] = []
    # Golden/Dead cross using MA5/MA20
    df["MA_CROSS"] = np.sign(df["MA5"] - df["MA20"]).diff()
    last_idx = df.index[-1]
    # Golden cross: sign diff from -1 to 1 -> diff == 2
    cross_rows = df[df["MA_CROSS"] == 2]
    if not cross_rows.empty:
        last_cross = cross_rows.iloc[-1]
        signals.append({
            "type": "golden_cross",
            "on": str(pd.to_datetime(last_cross["date"]).date()),
            "fast": "MA5",
            "slow": "MA20",
        })
    cross_rows_dead = df[df["MA_CROSS"] == -2]
    if not cross_rows_dead.empty:
        last_cross = cross_rows_dead.iloc[-1]
        signals.append({
            "type": "dead_cross",
            "on": str(pd.to_datetime(last_cross["date"]).date()),
            "fast": "MA5",
            "slow": "MA20",
        })

    # Price-Volume patterns (last day vs previous)
    if len(df) >= 2:
        d1 = df.iloc[-1]
        d0 = df.iloc[-2]
        price_up = d1["close"] > d0["close"]
        vol_up = d1["volume"] > d0["volume"]
        if price_up and vol_up:
            pv = "up_price_up_vol"
        elif price_up and not vol_up:
            pv = "up_price_down_vol"
        elif (not price_up) and vol_up:
            pv = "down_price_up_vol"
        elif (not price_up) and (not vol_up):
            pv = "down_price_down_vol"
        else:
            pv = "flat"
        signals.append({"type": "price_volume", "pattern": pv, "on": str(d1["date"].date())})

    out = {
        "stock_id": body.stock_id,
        "as_of": str(df["date"].max().date()),
        "indicators": {
            "MA5": round(float(df["MA5"].iloc[-1]), 4) if not pd.isna(df["MA5"].iloc[-1]) else None,
            "MA20": round(float(df["MA20"].iloc[-1]), 4) if not pd.isna(df["MA20"].iloc[-1]) else None,
            "MA60": round(float(df["MA60"].iloc[-1]), 4) if not pd.isna(df["MA60"].iloc[-1]) else None,
            "RSI14": round(float(df["RSI14"].iloc[-1]), 4) if not pd.isna(df["RSI14"].iloc[-1]) else None,
            "MACD": {
                "macd": round(float(df["MACD"].iloc[-1]), 4) if not pd.isna(df["MACD"].iloc[-1]) else None,
                "signal": round(float(df["MACD_SIGNAL"].iloc[-1]), 4) if not pd.isna(df["MACD_SIGNAL"].iloc[-1]) else None,
                "hist": round(float(df["MACD_HIST"].iloc[-1]), 4) if not pd.isna(df["MACD_HIST"].iloc[-1]) else None,
            },
            "ATR14": round(float(df["ATR14"].iloc[-1]), 4) if not pd.isna(df["ATR14"].iloc[-1]) else None,
        },
        "signals": signals,
    }
    return out