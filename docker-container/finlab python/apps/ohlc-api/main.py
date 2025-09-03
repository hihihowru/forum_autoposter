import os
import json
import pandas as pd
import finlab
from finlab import data
from datetime import datetime, timedelta
from fastapi import FastAPI, Query

app = FastAPI()

@app.on_event("startup")
def startup_event():
    api_key = os.getenv("FINLAB_API_KEY")
    if api_key:
        finlab.login(api_key)

@app.get("/get_ohlc")
def get_ohlc(stock_id: str = Query(..., description="股票代號，例如 '2330'")):
    try:
        open_df = data.get('price:開盤價')
        high_df = data.get('price:最高價')
        low_df = data.get('price:最低價')
        close_df = data.get('price:收盤價')
        volume_df = data.get('price:成交股數')

        if stock_id not in open_df.columns:
            return {"error": f"Stock ID {stock_id} not found."}

        ohlcv_df = pd.DataFrame({
            'open': open_df[stock_id],
            'high': high_df[stock_id],
            'low': low_df[stock_id],
            'close': close_df[stock_id],
            'volume': volume_df[stock_id]
        })

        ohlcv_df = ohlcv_df.dropna().reset_index()
        ohlcv_df.columns = ['date', 'open', 'high', 'low', 'close', 'volume']

        one_year_ago = datetime.today() - timedelta(days=365)
        ohlcv_df = ohlcv_df[ohlcv_df['date'] >= one_year_ago]

        return json.loads(ohlcv_df.to_json(orient="records", date_format="iso"))
    except Exception as e:
        return {"error": str(e)}