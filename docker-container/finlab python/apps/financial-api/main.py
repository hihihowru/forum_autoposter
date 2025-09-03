import os
import json
import pandas as pd
import finlab
from finlab import data
from datetime import datetime, timedelta
from fastapi import FastAPI, Query, HTTPException
from typing import Dict, Any, Optional

app = FastAPI()

@app.on_event("startup")
def startup_event():
    """啟動時登入 FinLab"""
    api_key = os.getenv("FINLAB_API_KEY")
    if api_key:
        finlab.login(api_key)

def format_large_number(num):
    """格式化大數字，例如 1204532131 -> 12億453萬"""
    if pd.isna(num) or num == 0:
        return "0"
    
    num = int(num)
    
    if num >= 100000000:  # 億
        yi = num // 100000000
        wan = (num % 100000000) // 10000
        if wan > 0:
            return f"{yi}億{wan}萬"
        else:
            return f"{yi}億"
    elif num >= 10000:  # 萬
        wan = num // 10000
        return f"{wan}萬"
    else:
        return str(num)

@app.get("/financial/{stock_id}")
def get_financial_data(stock_id: str, periods: int = Query(4, description="取得最近幾個季度的資料")):
    """取得股票財務資料"""
    try:
        # 取得各種財務指標
        operating_profit = data.get('fundamental_features:營業利益')
        ebitda = data.get('fundamental_features:EBITDA')
        operating_cash_flow = data.get('fundamental_features:營運現金流')
        net_profit = data.get('fundamental_features:歸屬母公司淨利')
        gross_margin = data.get('fundamental_features:營業毛利率')
        operating_margin = data.get('fundamental_features:營業利益率')
        pretax_margin = data.get('fundamental_features:稅前淨利率')
        net_margin = data.get('fundamental_features:稅後淨利率')
        current_assets = data.get('fundamental_features:流動資產')
        current_liabilities = data.get('fundamental_features:流動負債')
        roa = data.get('fundamental_features:ROA稅後息前')
        roe = data.get('fundamental_features:ROE稅後')
        
        if stock_id not in operating_profit.columns:
            raise HTTPException(status_code=404, detail=f"Stock ID {stock_id} not found")
        
        # 取得最近幾期的資料
        result = {
            "stock_id": stock_id,
            "data": []
        }
        
        for i in range(periods):
            try:
                # 取得各期資料
                period_data = {
                    "period": operating_profit.index[-(i+1)],
                    "profitability": {
                        "operating_profit": {
                            "value": int(operating_profit[stock_id].dropna().iloc[-(i+1)]),
                            "formatted": format_large_number(operating_profit[stock_id].dropna().iloc[-(i+1)])
                        },
                        "ebitda": {
                            "value": int(ebitda[stock_id].dropna().iloc[-(i+1)]),
                            "formatted": format_large_number(ebitda[stock_id].dropna().iloc[-(i+1)])
                        },
                        "net_profit": {
                            "value": int(net_profit[stock_id].dropna().iloc[-(i+1)]),
                            "formatted": format_large_number(net_profit[stock_id].dropna().iloc[-(i+1)])
                        }
                    },
                    "margins": {
                        "gross_margin": round(float(gross_margin[stock_id].dropna().iloc[-(i+1)]), 2),
                        "operating_margin": round(float(operating_margin[stock_id].dropna().iloc[-(i+1)]), 2),
                        "pretax_margin": round(float(pretax_margin[stock_id].dropna().iloc[-(i+1)]), 2),
                        "net_margin": round(float(net_margin[stock_id].dropna().iloc[-(i+1)]), 2)
                    },
                    "cash_flow": {
                        "operating_cash_flow": {
                            "value": int(operating_cash_flow[stock_id].dropna().iloc[-(i+1)]),
                            "formatted": format_large_number(operating_cash_flow[stock_id].dropna().iloc[-(i+1)])
                        }
                    },
                    "balance_sheet": {
                        "current_assets": {
                            "value": int(current_assets[stock_id].dropna().iloc[-(i+1)]),
                            "formatted": format_large_number(current_assets[stock_id].dropna().iloc[-(i+1)])
                        },
                        "current_liabilities": {
                            "value": int(current_liabilities[stock_id].dropna().iloc[-(i+1)]),
                            "formatted": format_large_number(current_liabilities[stock_id].dropna().iloc[-(i+1)])
                        }
                    },
                    "returns": {
                        "roa": round(float(roa[stock_id].dropna().iloc[-(i+1)]), 2),
                        "roe": round(float(roe[stock_id].dropna().iloc[-(i+1)]), 2)
                    }
                }
                
                result["data"].append(period_data)
                
            except IndexError:
                break
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/financial/{stock_id}/summary")
def get_financial_summary(stock_id: str):
    """取得股票財務摘要"""
    try:
        # 取得最新財務資料
        operating_profit = data.get('fundamental_features:營業利益')
        net_profit = data.get('fundamental_features:歸屬母公司淨利')
        gross_margin = data.get('fundamental_features:營業毛利率')
        operating_margin = data.get('fundamental_features:營業利益率')
        roe = data.get('fundamental_features:ROE稅後')
        current_assets = data.get('fundamental_features:流動資產')
        current_liabilities = data.get('fundamental_features:流動負債')
        
        if stock_id not in operating_profit.columns:
            raise HTTPException(status_code=404, detail=f"Stock ID {stock_id} not found")
        
        # 取得最新資料
        latest_profit = operating_profit[stock_id].dropna().iloc[-1]
        latest_net_profit = net_profit[stock_id].dropna().iloc[-1]
        latest_gross_margin = gross_margin[stock_id].dropna().iloc[-1]
        latest_operating_margin = operating_margin[stock_id].dropna().iloc[-1]
        latest_roe = roe[stock_id].dropna().iloc[-1]
        latest_current_assets = current_assets[stock_id].dropna().iloc[-1]
        latest_current_liabilities = current_liabilities[stock_id].dropna().iloc[-1]
        
        # 計算流動比率
        current_ratio = latest_current_assets / latest_current_liabilities if latest_current_liabilities > 0 else 0
        
        # 分析財務健康度
        profitability_status = "優秀" if latest_operating_margin > 15 else "良好" if latest_operating_margin > 10 else "一般"
        roe_status = "優秀" if latest_roe > 15 else "良好" if latest_roe > 10 else "一般"
        liquidity_status = "優秀" if current_ratio > 2 else "良好" if current_ratio > 1.5 else "一般"
        
        result = {
            "stock_id": stock_id,
            "latest_period": operating_profit.index[-1],
            "profitability": {
                "operating_profit": {
                    "value": int(latest_profit),
                    "formatted": format_large_number(latest_profit)
                },
                "net_profit": {
                    "value": int(latest_net_profit),
                    "formatted": format_large_number(latest_net_profit)
                },
                "gross_margin": round(float(latest_gross_margin), 2),
                "operating_margin": round(float(latest_operating_margin), 2),
                "roe": round(float(latest_roe), 2)
            },
            "liquidity": {
                "current_assets": {
                    "value": int(latest_current_assets),
                    "formatted": format_large_number(latest_current_assets)
                },
                "current_liabilities": {
                    "value": int(latest_current_liabilities),
                    "formatted": format_large_number(latest_current_liabilities)
                },
                "current_ratio": round(current_ratio, 2)
            },
            "analysis": {
                "profitability_status": profitability_status,
                "roe_status": roe_status,
                "liquidity_status": liquidity_status,
                "overall_health": "優秀" if all(s == "優秀" for s in [profitability_status, roe_status, liquidity_status]) else "良好"
            }
        }
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/financial/{stock_id}/ratios")
def get_financial_ratios(stock_id: str, periods: int = Query(4, description="取得最近幾個季度的財務比率")):
    """取得股票財務比率資料"""
    try:
        gross_margin = data.get('fundamental_features:營業毛利率')
        operating_margin = data.get('fundamental_features:營業利益率')
        pretax_margin = data.get('fundamental_features:稅前淨利率')
        net_margin = data.get('fundamental_features:稅後淨利率')
        roa = data.get('fundamental_features:ROA稅後息前')
        roe = data.get('fundamental_features:ROE稅後')
        
        if stock_id not in gross_margin.columns:
            raise HTTPException(status_code=404, detail=f"Stock ID {stock_id} not found")
        
        result = {
            "stock_id": stock_id,
            "ratios_data": []
        }
        
        for i in range(min(periods, len(gross_margin[stock_id].dropna()))):
            try:
                period_data = {
                    "period": gross_margin.index[-(i+1)],
                    "profitability_ratios": {
                        "gross_margin": round(float(gross_margin[stock_id].dropna().iloc[-(i+1)]), 2),
                        "operating_margin": round(float(operating_margin[stock_id].dropna().iloc[-(i+1)]), 2),
                        "pretax_margin": round(float(pretax_margin[stock_id].dropna().iloc[-(i+1)]), 2),
                        "net_margin": round(float(net_margin[stock_id].dropna().iloc[-(i+1)]), 2)
                    },
                    "return_ratios": {
                        "roa": round(float(roa[stock_id].dropna().iloc[-(i+1)]), 2),
                        "roe": round(float(roe[stock_id].dropna().iloc[-(i+1)]), 2)
                    }
                }
                result["ratios_data"].append(period_data)
            except IndexError:
                break
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    """健康檢查"""
    return {"status": "healthy", "service": "financial-api"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8009)


