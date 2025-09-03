# 虛擬 KOL 投資內容生成系統

## 🎯 系統目標

打造虛擬 KOL 內容生成系統，創造有料、有觀點、能增粉的投資內容。

### 核心功能
- **多角色 KOL**：不同投資風格和人格特質的虛擬 KOL
- **深度內容**：結合股價、營收、財報、歷史回測的專業分析
- **互動優化**：基於用戶互動數據自我學習和調整
- **增粉導向**：內容設計以吸引粉絲和引發互動為目標

### 虛擬 KOL 類型
1. **技術派 KOL**：專注技術分析、圖表解讀
2. **基本面 KOL**：專注財報分析、價值投資
3. **新聞驅動 KOL**：專注產業新聞、政策影響
4. **量化派 KOL**：專注數據分析、回測驗證
5. **教育型 KOL**：專注投資教育、風險管理

## 🏗️ 系統架構

```
apps/
├── ohlc-api/          # 股價資料 API
├── analyze-api/       # 技術指標分析
├── summary-api/       # 虛擬 KOL 內容生成 (LangGraph)
├── trainer/           # 互動學習與回測
packages/
└── shared/           # 共用 schemas 和工具
```

## 🚀 快速開始

### 環境設定
```bash
# 複製環境變數
cp .env.example .env
# 填入必要的 API keys
```

### 啟動服務
```bash
cd infra && docker compose up --build
```

### 測試虛擬 KOL
```bash
# 生成技術派 KOL 內容
curl -X POST http://localhost:8003/summarize \
  -H 'Content-Type: application/json' \
  -d '{
    "stock_id": "2330",
    "kol_persona": "technical",
    "content_style": "chart_analysis",
    "target_audience": "active_traders"
  }'
```

## 📊 內容生成流程

1. **資料收集** → 股價、財報、新聞、產業數據
2. **KOL 角色選擇** → 根據主題和時機選擇合適的 KOL
3. **內容生成** → LangGraph 多代理協作生成深度內容
4. **互動預測** → 預測內容的互動潛力
5. **發布與追蹤** → 發布內容並收集互動數據
6. **學習優化** → 基於互動數據調整 KOL 策略

## 🎭 KOL 人格系統

每個虛擬 KOL 都有獨特的：
- **投資風格**：技術派、基本面、量化等
- **表達方式**：專業、親民、教育性等
- **內容偏好**：圖表分析、財報解讀、新聞評論等
- **互動策略**：提問、分享、討論等