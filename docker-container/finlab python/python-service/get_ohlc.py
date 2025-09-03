import os
import json
import pandas as pd
import finlab
from fastapi import FastAPI, Query
from finlab import data
from datetime import datetime, timedelta

# 登入 API 金鑰
finlab.login(os.getenv("FINLAB_API_KEY"))

# 建立 FastAPI app
app = FastAPI()

@app.get("/get_ohlc")
def get_ohlc(stock_id: str = Query(..., description="股票代號，例如 '2330'")):
    try:
        # 讀取個別指標
        open_df = data.get('price:開盤價')
        high_df = data.get('price:最高價')
        low_df = data.get('price:最低價')
        close_df = data.get('price:收盤價')
        volume_df = data.get('price:成交股數')

        if stock_id not in open_df.columns:
            return {"error": f"Stock ID {stock_id} not found."}

        # 組成 OHLCV 表格
        ohlcv_df = pd.DataFrame({
            'open': open_df[stock_id],
            'high': high_df[stock_id],
            'low': low_df[stock_id],
            'close': close_df[stock_id],
            'volume': volume_df[stock_id]
        })

        # 資料清理：刪除缺值、重置 index
        ohlcv_df = ohlcv_df.dropna().reset_index()
        ohlcv_df.columns = ['date', 'open', 'high', 'low', 'close', 'volume']

        # 僅保留最近一年的資料
        one_year_ago = datetime.today() - timedelta(days=365)
        ohlcv_df = ohlcv_df[ohlcv_df['date'] >= one_year_ago]

        # 輸出成 JSON 格式（n8n 使用）
        return json.loads(ohlcv_df.to_json(orient="records", date_format="iso"))

    except Exception as e:
        return {"error": str(e)}