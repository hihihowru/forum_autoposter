# 虛擬 KOL 系統技術文檔

## 📚 目錄

- [系統概述](#系統概述)
- [架構設計](#架構設計)
- [服務詳解](#服務詳解)
- [API 文檔](#api-文檔)
- [部署指南](#部署指南)
- [開發指南](#開發指南)

---

## 🎯 系統概述

虛擬 KOL 系統是一個基於微服務架構的智能投資內容生成平台，能夠自動分析股票數據、生成技術分析報告，並以不同人格特質的虛擬 KOL 身份發布內容。

### 核心功能

- **多維度股票分析**: 技術指標、基本面分析、新聞影響
- **虛擬 KOL 人格**: 5種不同風格的投資專家人格
- **智能內容生成**: 基於數據分析的投資建議和報告
- **自動化發文**: 定時發布熱門話題相關內容
- **互動數據追蹤**: 監控內容表現和用戶互動

### 技術特點

- **微服務架構**: 6個獨立服務，各司其職
- **容器化部署**: Docker + Docker Compose
- **FastAPI 框架**: 高性能異步 API 服務
- **數據驅動**: 基於 FinLab 金融數據平台
- **可擴展設計**: 模組化架構，易於擴展

---

## 🏗️ 架構設計

### 系統架構圖

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Trending API  │    │   Summary API   │    │  Posting Service│
│   (熱門話題)     │    │   (內容生成)     │    │   (自動發文)     │
│   Port: 8005    │    │   Port: 8003    │    │   Port: 8006    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   OHLC API      │    │  Analyze API    │    │     Trainer     │
│   (股價數據)     │    │   (技術分析)     │    │   (回測訓練)     │
│   Port: 8001    │    │   Port: 8002    │    │   Port: 8004    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 服務依賴關係

- **OHLC API**: 基礎服務，提供股票價格數據
- **Analyze API**: 依賴 OHLC API，提供技術指標計算
- **Summary API**: 依賴 OHLC API 和 Analyze API，生成投資內容
- **Trending API**: 獨立服務，提供熱門話題和新聞
- **Posting Service**: 依賴多個 API，負責內容發布
- **Trainer**: 依賴 OHLC API 和 Analyze API，提供回測功能

---

## 🔧 服務詳解

### 1. OHLC API (Port: 8001)

**功能**: 提供股票開盤價、最高價、最低價、收盤價和成交量數據

**核心代碼**:
```python
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
```

**API 端點**:
- `GET /get_ohlc?stock_id={stock_id}`: 獲取指定股票的 OHLCV 數據

**數據來源**: FinLab 金融數據平台
**數據範圍**: 最近一年的日線數據

---

### 2. Analyze API (Port: 8002)

**功能**: 計算技術指標和生成交易信號

**核心技術指標**:
- **移動平均線**: MA5, MA20, MA60
- **RSI**: 相對強弱指數 (14日)
- **MACD**: 移動平均收斂發散指標
- **ATR**: 平均真實波幅 (14日)

**信號生成**:
- **黃金交叉/死亡交叉**: MA5 與 MA20 的交叉信號
- **價量關係**: 價格與成交量的配合模式

**核心代碼**:
```python
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
```

**API 端點**:
- `POST /analyze`: 分析股票數據並返回技術指標和信號

---

### 3. Summary API (Port: 8003)

**功能**: 生成虛擬 KOL 投資內容

**虛擬 KOL 人格**:

#### 技術大師 (Technical Master)
- **風格**: 專業且自信
- **專長**: 圖表分析、技術指標
- **語言**: 技術術語豐富，數據導向

#### 價值投資大師 (Value Guru)
- **風格**: 穩重且深思熟慮
- **專長**: 基本面分析、財報解讀
- **語言**: 邏輯清晰，重視數據

#### 新聞獵人 (News Hunter)
- **風格**: 敏銳且即時
- **專長**: 新聞影響、政策變化
- **語言**: 生動活潑，時事導向

#### 數據科學家 (Data Scientist)
- **風格**: 精確且客觀
- **專長**: 量化分析、回測驗證
- **語言**: 數據豐富，邏輯嚴謹

#### 投資導師 (Investment Teacher)
- **風格**: 親切且耐心
- **專長**: 投資教育、風險管理
- **語言**: 易懂親民，教育性強

**核心代碼**:
```python
def generate_technical_content(stock_id: str, indicators: Dict, signals: List, kol_persona: Dict) -> Dict[str, Any]:
    """生成技術派 KOL 內容"""
    ma5 = indicators.get("MA5", 0)
    ma20 = indicators.get("MA20", 0)
    rsi = indicators.get("RSI14", 0)
    macd_hist = indicators.get("MACD", {}).get("hist", 0)
    
    # 技術分析邏輯
    trend = "上升" if ma5 > ma20 else "下降"
    rsi_status = "超買" if rsi > 70 else "超賣" if rsi < 30 else "中性"
    
    title = f"📊 {stock_id} 技術面深度解析 - {kol_persona['name']}觀點"
    
    content_md = f"""
## 📈 {stock_id} 技術面分析報告

### 🎯 核心觀點
{stock_id} 目前處於**{trend}趨勢**，技術指標顯示**{rsi_status}**狀態。

### 📊 關鍵技術指標
- **MA5/MA20**: {ma5:.2f} / {ma20:.2f} ({'黃金交叉' if ma5 > ma20 else '死亡交叉'})
- **RSI14**: {rsi:.1f} ({rsi_status})
- **MACD柱狀體**: {macd_hist:.3f} ({'多頭' if macd_hist > 0 else '空頭'}訊號)

### 🔍 技術訊號分析
"""
    
    for signal in signals:
        if signal.get("type") == "golden_cross":
            content_md += f"- ✅ **黃金交叉**：{signal.get('fast')}上穿{signal.get('slow')}，多頭訊號確認\n"
        elif signal.get("type") == "price_volume":
            pattern = signal.get("pattern", "")
            if "up_price_up_vol" in pattern:
                content_md += "- 📈 **價漲量增**：買盤力道強勁，後市看好\n"
    
    content_md += f"""
### 💡 投資建議
基於技術分析，建議**{'買入' if trend == '上升' and rsi < 70 else '觀望' if rsi_status == '超買' else '賣出'}**。

### ⚠️ 風險提醒
- 技術分析僅供參考，請結合基本面
- 注意停損設定，建議在 {ma20:.2f} 附近
- 市場波動風險，投資需謹慎

---
*本內容由 {kol_persona['name']} 提供，僅供研究與教育用途*
"""
    
    return {
        "title": title,
        "content_md": content_md,
        "key_points": [
            f"{trend}趨勢確認",
            f"RSI {rsi_status}狀態", 
            f"MACD {'多頭' if macd_hist > 0 else '空頭'}訊號"
        ],
        "investment_advice": {
            "action": "buy" if trend == "上升" and rsi < 70 else "hold",
            "confidence": 0.75,
            "rationale": f"技術面顯示{trend}趨勢，RSI{rsi_status}",
            "risk": ["技術指標滯後性", "市場情緒變化"],
            "horizon_days": 20,
            "stops_targets": {"stop": 0.95, "target": 1.08}
        }
    }
```

**API 端點**:
- `POST /generate-kol-content`: 生成虛擬 KOL 內容
- `POST /summarize`: 向後相容的 summarize 端點
- `GET /kol-personas`: 獲取所有可用的 KOL 人格

---

### 4. Trending API (Port: 8005)

**功能**: 提供熱門話題、新聞素材和熱門股票

**核心功能**:
- **熱門話題**: 從 Cmoney 獲取市場熱點
- **新聞搜尋**: 整合多個新聞來源
- **熱門股票**: 基於熱度和成交量變化

**核心代碼**:
```python
@app.get("/trending", response_model=TrendingResponse)
async def get_trending_topics(
    limit: int = Query(10, description="獲取話題數量"),
    category: str = Query(None, description="話題分類")
):
    """獲取 Cmoney 熱門話題"""
    
    # 模擬 Cmoney API 回應 (實際整合時替換)
    trending_topics = [
        {
            "id": "topic_001",
            "title": "台積電法說會亮眼，AI需求強勁",
            "content": "台積電最新法說會顯示AI需求持續強勁，營收展望樂觀...",
            "stock_ids": ["2330", "2454", "3034"],
            "category": "earnings",
            "created_at": datetime.now() - timedelta(hours=2),
            "engagement_score": 0.85
        },
        {
            "id": "topic_002", 
            "title": "聯發科5G晶片市占率提升",
            "content": "聯發科在5G晶片市場表現亮眼，市占率持續提升...",
            "stock_ids": ["2454", "2379"],
            "category": "technology",
            "created_at": datetime.now() - timedelta(hours=4),
            "engagement_score": 0.72
        }
    ]
    
    # 根據分類篩選
    if category:
        trending_topics = [t for t in trending_topics if t["category"] == category]
    
    # 限制數量
    trending_topics = trending_topics[:limit]
    
    return TrendingResponse(
        topics=trending_topics,
        timestamp=datetime.now(),
        total_count=len(trending_topics)
    )
```

**API 端點**:
- `GET /trending`: 獲取熱門話題
- `GET /news/search`: 搜尋相關新聞
- `GET /news/stock/{stock_id}`: 獲取股票相關新聞
- `GET /trending/stocks`: 獲取熱門股票列表

---

### 5. Posting Service (Port: 8006)

**功能**: 自動化內容發布服務

**核心功能**:
- **自動發文**: 根據熱門話題自動生成並發布內容
- **手動發文**: 指定股票和 KOL 風格的手動發布
- **內容增強**: 整合新聞素材到投資內容中
- **平台整合**: 支援多個社交媒體平台

**核心代碼**:
```python
@app.post("/post/auto", response_model=PostingResult)
async def auto_post_content(background_tasks: BackgroundTasks, config: AutoPostingConfig):
    """自動發文 - 根據熱門話題自動生成內容並發文"""
    
    try:
        # 1. 獲取熱門話題
        trending_response = requests.get(f"{TRENDING_API_URL}/trending", params={"limit": 5})
        trending_response.raise_for_status()
        trending_topics = trending_response.json()
        
        if not trending_topics.get("topics"):
            return PostingResult(
                success=False,
                error="沒有找到熱門話題",
                timestamp=datetime.now()
            )
        
        # 2. 選擇第一個熱門話題
        topic = trending_topics["topics"][0]
        stock_id = topic["stock_ids"][0] if topic["stock_ids"] else "2330"
        
        # 3. 獲取相關新聞素材
        news_response = requests.get(f"{TRENDING_API_URL}/news/stock/{stock_id}", params={"limit": 3})
        news_items = []
        if news_response.status_code == 200:
            news_items = news_response.json().get("news", [])
        
        # 4. 生成KOL內容
        content_request = {
            "stock_id": stock_id,
            "kol_persona": config.kol_personas[0],
            "content_style": "chart_analysis",
            "target_audience": "active_traders"
        }
        
        summary_response = requests.post(f"{SUMMARY_API_URL}/generate-kol-content", json=content_request)
        summary_response.raise_for_status()
        kol_content = summary_response.json()
        
        # 5. 整合新聞素材到內容中
        enhanced_content = enhance_content_with_news(kol_content, topic, news_items)
        
        # 6. 發文到指定平台
        if config.enabled:
            background_tasks.add_task(post_to_platform, enhanced_content, topic)
        
        return PostingResult(
            success=True,
            post_id=f"post_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            content=enhanced_content,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        return PostingResult(
            success=False,
            error=str(e),
            timestamp=datetime.now()
        )
```

**API 端點**:
- `POST /post/auto`: 自動發文
- `POST /post/manual`: 手動發文
- `GET /health`: 健康檢查
- `GET /trending/preview`: 預覽熱門話題內容

---

### 6. Trainer (Port: 8004)

**功能**: 策略回測和反饋學習

**核心功能**:
- **策略回測**: 基於歷史數據驗證投資策略
- **反饋記錄**: 追蹤內容表現和用戶互動
- **績效評估**: 計算各種投資指標

**核心代碼**:
```python
@app.post("/backtest")
def backtest(body: BacktestIn):
    return {
        "CAGR": 0.12,
        "MaxDD": -0.18,
        "WinRate": 0.54,
        "Sharpe": 1.1,
        "params": body.rules,
    }

@app.post("/log-feedback")
def log_feedback(body: FeedbackIn):
    return {"ok": True, "received": body.model_dump()}
```

**API 端點**:
- `POST /backtest`: 執行策略回測
- `POST /log-feedback`: 記錄用戶反饋

---

## 📖 API 文檔

### 通用響應格式

所有 API 都遵循統一的響應格式：

```json
{
  "success": true,
  "data": {...},
  "timestamp": "2024-01-01T00:00:00Z",
  "error": null
}
```

### 錯誤處理

```json
{
  "success": false,
  "data": null,
  "timestamp": "2024-01-01T00:00:00Z",
  "error": "錯誤描述"
}
```

### 認證

目前系統使用環境變數進行 API 密鑰管理：

```bash
FINLAB_API_KEY=your_finlab_api_key
CMONEY_API_KEY=your_cmoney_api_key
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key
NEWS_API_KEY=your_news_api_key
```

---

## 🚀 部署指南

### 環境要求

- Docker 20.10+
- Docker Compose 2.0+
- 至少 4GB RAM
- 穩定的網路連接

### 快速部署

1. **克隆專案**
```bash
git clone <repository_url>
cd finlab-python
```

2. **配置環境變數**
```bash
cp .env.example .env
# 編輯 .env 文件，填入必要的 API 密鑰
```

3. **啟動服務**
```bash
# 使用完整架構
docker-compose -f infra/compose.yaml up -d

# 或使用基礎版本
docker-compose up -d
```

4. **驗證部署**
```bash
# 檢查所有服務狀態
docker-compose ps

# 測試 API 健康檢查
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health
curl http://localhost:8005/health
curl http://localhost:8006/health
curl http://localhost:8004/health
```

### 服務端口映射

| 服務 | 內部端口 | 外部端口 | 說明 |
|------|----------|----------|------|
| OHLC API | 8000 | 8001 | 股票價格數據 |
| Analyze API | 8000 | 8002 | 技術分析 |
| Summary API | 8000 | 8003 | 內容生成 |
| Trainer | 8000 | 8004 | 回測訓練 |
| Trending API | 8000 | 8005 | 熱門話題 |
| Posting Service | 8000 | 8006 | 自動發文 |

---

## 🛠️ 開發指南

### 本地開發環境

1. **安裝依賴**
```bash
# 創建虛擬環境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安裝依賴
pip install -r requirements.txt
```

2. **運行單個服務**
```bash
# 例如運行 Summary API
cd apps/summary-api
uvicorn main:app --reload --host 0.0.0.0 --port 8003
```

### 代碼結構

```
finlab-python/
├── apps/                    # 微服務應用
│   ├── ohlc-api/          # 股票數據服務
│   ├── analyze-api/       # 技術分析服務
│   ├── summary-api/       # 內容生成服務
│   ├── trending-api/      # 熱門話題服務
│   ├── posting-service/   # 自動發文服務
│   └── trainer/           # 回測訓練服務
├── packages/               # 共享套件
│   └── shared/            # 共享工具和模型
├── infra/                  # 基礎設施配置
│   └── compose.yaml       # Docker Compose 配置
└── docker-compose.yml      # 基礎 Docker Compose 配置
```

### 開發最佳實踐

1. **API 設計**
   - 使用 Pydantic 模型進行數據驗證
   - 統一的錯誤處理和響應格式
   - 完整的 API 文檔和類型提示

2. **代碼品質**
   - 遵循 PEP 8 編碼規範
   - 完整的函數和類文檔字符串
   - 單元測試覆蓋關鍵功能

3. **微服務設計**
   - 服務間鬆耦合，通過 API 通信
   - 每個服務專注於單一職責
   - 使用環境變數進行配置管理

### 測試

```bash
# 運行所有測試
pytest

# 運行特定服務的測試
pytest apps/summary-api/tests/

# 生成測試覆蓋率報告
pytest --cov=apps --cov-report=html
```

---

## 📊 監控和日誌

### 健康檢查

每個服務都提供健康檢查端點：

```bash
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health
curl http://localhost:8004/health
curl http://localhost:8005/health
curl http://localhost:8006/health
```

### 日誌查看

```bash
# 查看特定服務的日誌
docker-compose logs ohlc-api
docker-compose logs analyze-api
docker-compose logs summary-api

# 查看所有服務的日誌
docker-compose logs -f
```

---

## 🔮 未來規劃

### 短期目標 (1-3個月)

- [ ] 整合真實的 Cmoney API
- [ ] 添加更多技術指標
- [ ] 實現用戶反饋學習機制
- [ ] 優化內容生成品質

### 中期目標 (3-6個月)

- [ ] 支援更多股票市場
- [ ] 實現機器學習模型訓練
- [ ] 添加回測結果可視化
- [ ] 支援多語言內容生成

### 長期目標 (6-12個月)

- [ ] 實現預測模型
- [ ] 支援期貨和選擇權分析
- [ ] 實現社交媒體自動化營銷
- [ ] 建立完整的投資組合管理系統

---

## 📞 支援和聯繫

### 技術支援

- **GitHub Issues**: 報告 Bug 和功能請求
- **文檔**: 本文檔和 API 參考
- **社群**: 開發者論壇和討論群組

### 貢獻指南

我們歡迎所有形式的貢獻：

1. Fork 專案
2. 創建功能分支
3. 提交變更
4. 發起 Pull Request

### 授權

本專案採用 MIT 授權條款，詳見 LICENSE 文件。

---

## 📝 更新日誌

### v1.0.0 (2024-01-01)
- 初始版本發布
- 實現基礎微服務架構
- 支援 5 種虛擬 KOL 人格
- 完整的技術分析功能
- Docker 容器化部署

---

*最後更新: 2024-01-01*
*文檔版本: v1.0.0*

