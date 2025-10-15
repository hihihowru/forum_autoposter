import os
import json
import pandas as pd
import finlab
from finlab import data
from datetime import datetime, timedelta
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import numpy as np

app = FastAPI()

# 添加 CORS 中間件
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://forum-autoposter-dz27.vercel.app",
        "https://forum-autoposter-dz27-git-test-will-cs-projects-2b6e293d.vercel.app",
        "https://forum-autoposter-dz27-p6dtkgkw9-will-cs-projects-2b6e293d.vercel.app",
        "http://localhost:3000",
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    api_key = os.getenv("FINLAB_API_KEY")
    if api_key:
        finlab.login(api_key)
        print("✅ FinLab API 登入成功")
    else:
        print("❌ 未找到 FINLAB_API_KEY 環境變數")

def ensure_finlab_login():
    """確保 FinLab 已登入"""
    try:
        # 嘗試獲取一個簡單的數據來檢查是否已登入
        test_data = data.get('market_transaction_info:收盤指數')
        if test_data is None:
            # 如果獲取失敗，重新登入
            api_key = os.getenv("FINLAB_API_KEY")
            if api_key:
                finlab.login(api_key)
                print("🔄 FinLab API 重新登入成功")
            else:
                raise Exception("未找到 FINLAB_API_KEY")
    except Exception as e:
        print(f"❌ FinLab 登入檢查失敗: {e}")
        raise e

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

@app.get("/industries")
def get_all_industries_endpoint():
    """獲取所有產業類別"""
    try:
        industries = get_all_industries()
        return {
            "success": True,
            "industries": industries,
            "total_count": len(industries)
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/stocks_by_industry")
def get_stocks_by_industry(
    industries: str = Query("", description="產業類別，多個用逗號分隔"),
    limit: int = Query(1000, description="股票數量限制")
):
    """根據產業類別獲取股票列表"""
    try:
        # 解析產業類別參數
        selected_industries = []
        if industries:
            selected_industries = [industry.strip() for industry in industries.split(',') if industry.strip()]
        
        # 獲取所有股票代號
        all_stock_codes = list(stock_mapping.keys())
        
        # 根據產業篩選
        if selected_industries:
            filtered_codes = filter_stocks_by_industry(all_stock_codes, selected_industries)
        else:
            filtered_codes = all_stock_codes
        
        # 限制數量
        filtered_codes = filtered_codes[:limit]
        
        # 構建股票資訊
        stocks = []
        for stock_code in filtered_codes:
            stock_name = get_stock_name(stock_code)
            industry = get_stock_industry(stock_code)
            
            stocks.append({
                'stock_code': stock_code,
                'stock_name': stock_name,
                'industry': industry
            })
        
        return {
            "success": True,
            "stocks": stocks,
            "total_count": len(stocks),
            "selected_industries": selected_industries
        }
        
    except Exception as e:
        return {"error": str(e)}

@app.get("/after_hours_limit_up")
def get_after_hours_limit_up_stocks(
    limit: int = Query(1000, description="股票數量限制（設為大數值以獲取所有符合條件的股票）"),
    changeThreshold: float = Query(9.5, description="漲跌幅閾值百分比"),
    industries: str = Query("", description="產業類別篩選，多個用逗號分隔")
):
    """獲取盤後漲停股票列表 - 支持動態漲跌幅設定"""
    try:
        # 獲取收盤價數據
        close_df = data.get('price:收盤價')
        volume_df = data.get('price:成交股數')
        
        if close_df is None or close_df.empty:
            return {"error": "無法獲取收盤價數據"}
        
        # 確保數據按日期排序
        close_df = close_df.sort_index()
        if volume_df is not None:
            volume_df = volume_df.sort_index()
        
        # 獲取最新交易日數據
        latest_date = close_df.index[-1]
        latest_close = close_df.loc[latest_date]
        
        # 修復：獲取前一交易日數據
        previous_dates = close_df.index[close_df.index < latest_date]
        if len(previous_dates) == 0:
            return {"error": f"無法找到 {latest_date.strftime('%Y-%m-%d')} 之前的交易日數據"}
        
        previous_date = previous_dates[-1]
        previous_close = close_df.loc[previous_date]
        
        # 獲取最新成交量數據
        latest_volume = None
        if volume_df is not None and latest_date in volume_df.index:
            latest_volume = volume_df.loc[latest_date]
        
        # 解析產業類別參數
        selected_industries = []
        if industries:
            selected_industries = [industry.strip() for industry in industries.split(',') if industry.strip()]
        
        # 找出漲停股票 (比較最後一row和倒數第二row的差異)
        limit_up_stocks = []
        
        for stock_id in latest_close.index:
            try:
                # 產業篩選
                if selected_industries:
                    stock_industry = get_stock_industry(stock_id)
                    if stock_industry not in selected_industries:
                        continue
                
                # 獲取今日和昨日收盤價
                today_price = latest_close[stock_id]
                yesterday_price = previous_close[stock_id]
                
                # 檢查是否有有效數據
                if pd.isna(today_price) or pd.isna(yesterday_price) or yesterday_price == 0:
                    continue
                
                # 計算漲幅
                change_percent = ((today_price - yesterday_price) / yesterday_price) * 100
                
                # 檢查是否漲停 (漲幅 >= changeThreshold%)
                if change_percent >= changeThreshold:
                    stock_name = get_stock_name(stock_id)
                    stock_industry = get_stock_industry(stock_id)
                    
                    # 獲取成交量
                    volume = 0
                    if latest_volume is not None and stock_id in latest_volume.index:
                        vol = latest_volume[stock_id]
                        if not pd.isna(vol):
                            volume = int(vol)
                    
                    # 計算過去五個交易日的統計資訊
                    trading_stats = calculate_trading_stats(stock_id, latest_date, close_df)
                    
                    limit_up_stocks.append({
                        'stock_code': stock_id,
                        'stock_name': stock_name,
                        'industry': stock_industry,  # 新增產業欄位
                        'current_price': float(today_price),  # 移除 $ 符號
                        'yesterday_close': float(yesterday_price),
                        'change_amount': float(today_price - yesterday_price),
                        'change_percent': float(change_percent),
                        'volume': volume,
                        'date': latest_date.strftime('%Y-%m-%d'),
                        'previous_date': previous_date.strftime('%Y-%m-%d'),
                        'up_days_5': trading_stats['up_days'],  # 過去五個交易日上漲天數
                        'five_day_change': trading_stats['five_day_change']  # 五日漲跌幅
                    })
                    
            except Exception as e:
                print(f"處理股票 {stock_id} 時發生錯誤: {e}")
                continue
        
        # 按成交量排序，取前N檔
        limit_up_stocks.sort(key=lambda x: x['volume'], reverse=True)
        limit_up_stocks = limit_up_stocks[:limit]
        
        return {
            'success': True,
            'total_count': len(limit_up_stocks),
            'stocks': limit_up_stocks,
            'timestamp': datetime.now().isoformat(),
            'date': latest_date.strftime('%Y-%m-%d'),
            'previous_date': previous_date.strftime('%Y-%m-%d'),
            'changeThreshold': changeThreshold
        }
        
    except Exception as e:
        return {"error": str(e)}

# 載入股票映射表
def load_stock_mapping():
    try:
        with open('/app/stock_mapping.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"載入股票映射表失敗: {e}")
        return {}

# 全域變數
stock_mapping = load_stock_mapping()

def get_stock_name(stock_code: str) -> str:
    """根據股票代號獲取股票名稱"""
    # 先從映射表查找
    if stock_code in stock_mapping:
        return stock_mapping[stock_code].get('company_name', f"股票{stock_code}")
    
    # 如果映射表中沒有，使用原本的硬編碼映射
    stock_names = {
        "2330": "台積電", "2454": "聯發科", "2317": "鴻海", "2881": "富邦金",
        "2882": "國泰金", "1101": "台泥", "1102": "亞泥", "1216": "統一",
        "1303": "南亞", "1326": "台化", "2002": "中鋼", "2308": "台達電",
        "2377": "微星", "2382": "廣達", "2408": "南亞科", "2474": "可成",
        "2498": "宏達電", "3008": "大立光", "3034": "聯詠", "3231": "緯創",
        "3711": "日月光投控", "4938": "和碩", "6505": "台塑化", "8046": "南電",
        "9910": "豐泰", "2412": "中華電", "1301": "台塑", "2603": "長榮"
    }
    return stock_names.get(stock_code, f"股票{stock_code}")

def get_stock_industry(stock_code: str) -> str:
    """根據股票代號獲取產業類別"""
    if stock_code in stock_mapping:
        return stock_mapping[stock_code].get('industry', '未知產業')
    return '未知產業'

def get_all_industries() -> list:
    """獲取所有產業類別"""
    industries = set()
    for stock_code, info in stock_mapping.items():
        if 'industry' in info:
            industries.add(info['industry'])
    return sorted(list(industries))

def filter_stocks_by_industry(stock_codes: list, selected_industries: list) -> list:
    """根據產業類別篩選股票"""
    if not selected_industries:
        return stock_codes
    
    filtered_codes = []
    for stock_code in stock_codes:
        industry = get_stock_industry(stock_code)
        if industry in selected_industries:
            filtered_codes.append(stock_code)
    
    return filtered_codes

def calculate_trading_stats(stock_id: str, latest_date: datetime, close_df: pd.DataFrame) -> dict:
    """計算過去五個交易日的統計資訊"""
    try:
        # 獲取過去5個交易日的數據
        trading_days = close_df.index[close_df.index <= latest_date].sort_values(ascending=False)[:5]
        
        if len(trading_days) < 2:
            return {"up_days": 0, "five_day_change": 0.0}
        
        # 計算上漲天數
        up_days = 0
        for i in range(len(trading_days) - 1):
            current_price = close_df.loc[trading_days[i], stock_id]
            previous_price = close_df.loc[trading_days[i + 1], stock_id]
            
            if not pd.isna(current_price) and not pd.isna(previous_price) and current_price > previous_price:
                up_days += 1
        
        # 計算五日前的漲跌幅
        five_days_ago_price = close_df.loc[trading_days[-1], stock_id]
        latest_price = close_df.loc[trading_days[0], stock_id]
        
        if not pd.isna(five_days_ago_price) and not pd.isna(latest_price) and five_days_ago_price != 0:
            five_day_change = ((latest_price - five_days_ago_price) / five_days_ago_price) * 100
        else:
            five_day_change = 0.0
            
        return {
            "up_days": up_days,
            "five_day_change": round(five_day_change, 2)
        }
    except Exception as e:
        print(f"計算 {stock_id} 交易統計失敗: {e}")
        return {"up_days": 0, "five_day_change": 0.0}

@app.get("/trending-stocks/info")
def get_trending_stocks_info(stock_codes: str = Query(..., description="股票代號列表，用逗號分隔")):
    """獲取熱門話題股票的完整資訊"""
    try:
        ensure_finlab_login()
        
        # 解析股票代號
        stock_list = [code.strip() for code in stock_codes.split(',') if code.strip()]
        if not stock_list:
            return {"error": "請提供有效的股票代號"}
        
        result = []
        
        for stock_code in stock_list:
            try:
                # 獲取基本資訊
                stock_info = {
                    "code": stock_code,
                    "name": get_stock_name(stock_code),
                    "industry": get_stock_industry(stock_code),
                    "type": "index_future" if stock_code == "TWA00" else "stock"
                }
                
                # 特殊處理 TWA00
                if stock_code == "TWA00":
                    # 直接獲取台指期市場資訊
                    try:
                        market_transaction_info = data.get('market_transaction_info:收盤指數')
                        if market_transaction_info is not None and len(market_transaction_info.index) > 0:
                            latest_date = market_transaction_info.index[-1]
                            taiex_closing = market_transaction_info.loc[latest_date, "TAIEX"] if "TAIEX" in market_transaction_info.columns else 0
                            
                            # 計算漲跌百分比
                            taiex_change = 0.0
                            if len(market_transaction_info.index) > 1:
                                previous_date = market_transaction_info.index[-2]
                                taiex_previous = market_transaction_info.loc[previous_date, "TAIEX"] if "TAIEX" in market_transaction_info.columns else 0
                                if taiex_previous > 0:
                                    taiex_change = ((taiex_closing - taiex_previous) / taiex_previous) * 100
                            
                            stock_info.update({
                                "market_data": {
                                    "closing_index": float(taiex_closing),
                                    "change_percent": float(taiex_change)
                                },
                                "date": latest_date.strftime('%Y-%m-%d'),
                                "data_source": "market_transaction_info"
                            })
                    except Exception as e:
                        print(f"獲取 TWA00 資訊失敗: {e}")
                        stock_info["error"] = f"獲取 TWA00 資訊失敗: {str(e)}"
                else:
                    # 獲取個股資訊
                    try:
                        # 嘗試不同的數據格式
                        price_data = None
                        volume_data = None
                        
                        # 嘗試獲取價格數據
                        for price_key in [f'{stock_code}:收盤價', f'{stock_code}:close', 'close']:
                            try:
                                price_data = data.get(price_key)
                                if price_data is not None and len(price_data.index) > 0:
                                    break
                            except:
                                continue
                        
                        if price_data is not None and len(price_data.index) > 0:
                            latest_date = price_data.index[-1]
                            
                            # 嘗試不同的列名
                            closing_price = 0
                            for col in price_data.columns:
                                if stock_code in str(col) or col == stock_code:
                                    closing_price = price_data.loc[latest_date, col]
                                    break
                            
                            if closing_price == 0 and len(price_data.columns) > 0:
                                # 如果找不到對應列，使用第一列
                                closing_price = price_data.iloc[-1, 0]
                            
                            # 計算漲跌百分比
                            change_percent = 0.0
                            if len(price_data.index) > 1:
                                prev_date = price_data.index[-2]
                                prev_price = 0
                                for col in price_data.columns:
                                    if stock_code in str(col) or col == stock_code:
                                        prev_price = price_data.loc[prev_date, col]
                                        break
                                if prev_price == 0 and len(price_data.columns) > 0:
                                    prev_price = price_data.iloc[-2, 0]
                                
                                if prev_price > 0:
                                    change_percent = ((closing_price - prev_price) / prev_price) * 100
                            
                            stock_info.update({
                                "market_data": {
                                    "closing_price": float(closing_price),
                                    "change_percent": float(change_percent),
                                    "date": latest_date.strftime('%Y-%m-%d')
                                }
                            })
                        
                        # 嘗試獲取成交量數據
                        for volume_key in [f'{stock_code}:成交量', f'{stock_code}:volume', 'volume']:
                            try:
                                volume_data = data.get(volume_key)
                                if volume_data is not None and len(volume_data.index) > 0:
                                    break
                            except:
                                continue
                        
                        if volume_data is not None and len(volume_data.index) > 0:
                            latest_date = volume_data.index[-1]
                            volume = 0
                            for col in volume_data.columns:
                                if stock_code in str(col) or col == stock_code:
                                    volume = volume_data.loc[latest_date, col]
                                    break
                            if volume == 0 and len(volume_data.columns) > 0:
                                volume = volume_data.iloc[-1, 0]
                            stock_info["volume"] = float(volume)
                        
                        # 如果沒有獲取到詳細數據，至少提供基本資訊
                        if "market_data" not in stock_info:
                            stock_info["note"] = "僅提供基本資訊，詳細市場數據暫不可用"
                            
                    except Exception as e:
                        print(f"獲取股票 {stock_code} 詳細資訊失敗: {e}")
                        stock_info["note"] = f"詳細資訊獲取失敗: {str(e)}"
                
                result.append(stock_info)
                
            except Exception as e:
                result.append({
                    "code": stock_code,
                    "error": f"獲取股票資訊失敗: {str(e)}"
                })
        
        return {
            "stocks": result,
            "total_count": len(result),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {"error": f"獲取熱門話題股票資訊失敗: {str(e)}"}

@app.get("/twa00/market_info")
def get_twa00_market_info():
    """獲取台指期市場資訊 (TWA00)"""
    try:
        # 確保 FinLab 已登入
        ensure_finlab_login()
        
        # 獲取 TAIEX 市場交易資訊（主要數據源）
        market_transaction_info = data.get('market_transaction_info:收盤指數')
        
        # 檢查數據是否可用
        if market_transaction_info is None or len(market_transaction_info.index) == 0:
            return {"error": "無法獲取台指期價格數據"}
        
        # 獲取最新數據
        latest_date = market_transaction_info.index[-1]
        
        # 安全地獲取數據
        def safe_get_value(df, date, column_name):
            if df is None or len(df.index) == 0:
                return 0
            try:
                if column_name in df.columns:
                    value = df.loc[date, column_name]
                    if pd.isna(value):
                        return 0
                    return value
                return 0
            except:
                return 0
        
        # 使用正確的 TAIEX 列名
        taiex_column = "TAIEX"  # 台股加權指數
        taiex_closing = safe_get_value(market_transaction_info, latest_date, taiex_column)
        
        # 計算漲跌百分比（與前一日比較）
        taiex_change = 0.0
        if len(market_transaction_info.index) > 1:
            previous_date = market_transaction_info.index[-2]
            taiex_previous = safe_get_value(market_transaction_info, previous_date, taiex_column)
            if taiex_previous > 0:
                taiex_change = ((taiex_closing - taiex_previous) / taiex_previous) * 100
        
        result = {
            "symbol": "TWA00",
            "name": "台指期",
            "date": latest_date.strftime('%Y-%m-%d'),
            "taiex_data": {
                "closing_index": float(taiex_closing),
                "change_percent": float(taiex_change)
            },
            "data_source": "market_transaction_info",
            "column_used": taiex_column,
            "note": "使用台股加權指數數據作為台指期參考"
        }
        
        return result
        
    except Exception as e:
        return {"error": f"獲取台指期數據失敗: {str(e)}"}

@app.get("/twa00/historical")
def get_twa00_historical(days: int = Query(30, description="獲取最近幾天的歷史數據")):
    """獲取台指期歷史數據"""
    try:
        # 確保 FinLab 已登入
        ensure_finlab_login()
        
        # 獲取收盤指數歷史數據
        closing_index = data.get('market_transaction_info:收盤指數')
        index_change_percent = data.get('stock_index_price:漲跌百分比(%)')
        
        if closing_index is None or len(closing_index.index) == 0:
            return {"error": "無法獲取台指期歷史數據"}
        
        # 獲取最近 N 天的數據
        recent_data = closing_index.tail(days)
        
        historical_data = []
        for date, value in recent_data.items():
            if not pd.isna(value):
                change_percent = 0.0
                if index_change_percent is not None and date in index_change_percent.index:
                    change_percent = float(index_change_percent.loc[date]) if not pd.isna(index_change_percent.loc[date]) else 0.0
                
                historical_data.append({
                    "date": date.strftime('%Y-%m-%d'),
                    "closing_index": float(value),
                    "change_percent": change_percent
                })
        
        return {
            "symbol": "TWA00",
            "name": "台指期",
            "historical_data": historical_data,
            "total_days": len(historical_data)
        }
        
    except Exception as e:
        return {"error": f"獲取台指期歷史數據失敗: {str(e)}"}

@app.get("/debug/market_transaction_info")
def debug_market_transaction_info():
    """調試 market_transaction_info 表格結構"""
    try:
        ensure_finlab_login()
        
        # 獲取市場交易資訊
        market_closing = data.get('market_transaction_info:收盤指數')
        market_volume = data.get('market_transaction_info:成交股數')
        market_amount = data.get('market_transaction_info:成交金額')
        market_count = data.get('market_transaction_info:成交筆數')
        
        def safe_dict_convert(df):
            if df is None:
                return None
            try:
                df_clean = df.fillna(0)
                return df_clean.head(3).to_dict()
            except:
                return "無法轉換為字典"
        
        result = {
            "closing_index_info": {
                "is_none": market_closing is None,
                "shape": market_closing.shape if market_closing is not None else None,
                "columns": list(market_closing.columns) if market_closing is not None else None,
                "index": [str(x) for x in list(market_closing.index)[-5:]] if market_closing is not None else None,
                "sample_data": safe_dict_convert(market_closing)
            },
            "volume_info": {
                "is_none": market_volume is None,
                "shape": market_volume.shape if market_volume is not None else None,
                "columns": list(market_volume.columns) if market_volume is not None else None,
                "sample_data": safe_dict_convert(market_volume)
            },
            "amount_info": {
                "is_none": market_amount is None,
                "shape": market_amount.shape if market_amount is not None else None,
                "columns": list(market_amount.columns) if market_amount is not None else None,
                "sample_data": safe_dict_convert(market_amount)
            },
            "count_info": {
                "is_none": market_count is None,
                "shape": market_count.shape if market_count is not None else None,
                "columns": list(market_count.columns) if market_count is not None else None,
                "sample_data": safe_dict_convert(market_count)
            }
        }
        
        return result
        
    except Exception as e:
        return {"error": f"調試失敗: {str(e)}"}

@app.get("/debug/stock_index_price")
def debug_stock_index_price():
    """調試 stock_index_price 表格結構"""
    try:
        ensure_finlab_login()
        
        # 獲取指數價格資訊
        index_closing_price = data.get('stock_index_price:收盤指數')
        index_change_percent = data.get('stock_index_price:漲跌百分比(%)')
        
        def safe_dict_convert(df):
            if df is None:
                return None
            try:
                # 轉換為字典，處理 NaN 值
                df_clean = df.fillna(0)
                return df_clean.head(3).to_dict()
            except:
                return "無法轉換為字典"
        
        result = {
            "closing_price_info": {
                "is_none": index_closing_price is None,
                "shape": index_closing_price.shape if index_closing_price is not None else None,
                "columns": list(index_closing_price.columns) if index_closing_price is not None else None,
                "index": [str(x) for x in list(index_closing_price.index)[-5:]] if index_closing_price is not None else None,
                "sample_data": safe_dict_convert(index_closing_price)
            },
            "change_percent_info": {
                "is_none": index_change_percent is None,
                "shape": index_change_percent.shape if index_change_percent is not None else None,
                "columns": list(index_change_percent.columns) if index_change_percent is not None else None,
                "index": [str(x) for x in list(index_change_percent.index)[-5:]] if index_change_percent is not None else None,
                "sample_data": safe_dict_convert(index_change_percent)
            }
        }
        
        return result
        
    except Exception as e:
        return {"error": f"調試失敗: {str(e)}"}

@app.get("/get_stock_name")
def get_stock_name_api(stock_id: str = Query(..., description="股票代號")):
    """根據股票代號獲取股票名稱"""
    try:
        # 特殊處理 TWA00
        if stock_id == "TWA00":
            return {
                "code": "TWA00",
                "name": "台指期",
                "industry": "期貨",
                "type": "index_future"
            }
        
        # 使用現有的 get_stock_name 函數
        name = get_stock_name(stock_id)
        industry = get_stock_industry(stock_id)
        
        return {
            "code": stock_id,
            "name": name,
            "industry": industry,
            "type": "stock"
        }
        
    except Exception as e:
        return {"error": f"獲取股票名稱失敗: {str(e)}"}