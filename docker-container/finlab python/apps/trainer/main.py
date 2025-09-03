from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Any

app = FastAPI()

class BacktestIn(BaseModel):
    rules: Dict[str, Any]
    start: str
    end: str
    stock_ids: List[str]

@app.post("/backtest")
def backtest(body: BacktestIn):
    return {
        "CAGR": 0.12,
        "MaxDD": -0.18,
        "WinRate": 0.54,
        "Sharpe": 1.1,
        "params": body.rules,
    }

class FeedbackIn(BaseModel):
    stock_id: str
    post_id: str
    clicks: int
    saves: int
    ctr: float | None = None
    pnl_at_horizon: float | None = None

@app.post("/log-feedback")
def log_feedback(body: FeedbackIn):
    return {"ok": True, "received": body.model_dump()}