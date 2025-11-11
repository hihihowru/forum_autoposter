# 自動按讚機器人功能 - 完整文件

**創建日期**: 2025-11-10
**作者**: Claude Code
**狀態**: 已完成 ✅

---

## 📋 目錄

1. [功能概述](#功能概述)
2. [系統架構](#系統架構)
3. [核心演算法 - Poisson 分佈](#核心演算法---poisson-分佈)
4. [資料庫結構](#資料庫結構)
5. [後端 API](#後端-api)
6. [前端 UI](#前端-ui)
7. [使用流程](#使用流程)
8. [部署指南](#部署指南)
9. [測試計畫](#測試計畫)
10. [待辦事項](#待辦事項)

---

## 功能概述

### 核心功能
自動按讚機器人是一個智能化的互動管理系統，能夠：

1. **接收文章串流**：每小時獲取新創建的文章 ID
2. **智能分配反應**：使用 Poisson 分佈演算法隨機分配按讚數量
3. **模擬自然行為**：避免過於規律的反應模式，模擬真實用戶行為
4. **多 KOL 協作**：從選定的 KOL 池中分配按讚任務
5. **完整記錄**：追蹤所有反應活動，提供詳細統計數據

### 核心概念

**反應倍數 (Reaction Percentage)**
- 100% = 1 倍反應 (6000 篇文章 → 6000 個讚)
- 200% = 2 倍反應 (6000 篇文章 → 12000 個讚)
- 可設定 0% - 1000%

**隨機分佈**
- 使用 **Poisson 分佈**確保自然隨機性
- 部分文章獲得 0 個讚
- 部分文章獲得 1-2 個讚
- 少數文章獲得 3+ 個讚
- **均勻且隨機**，避免集中在少數文章

**KOL 池 (KOL Pool)**
- 選擇哪些 KOL 帳號可以執行按讚
- 支援多選
- 隨機分配給不同 KOL 執行

---

## 系統架構

```
┌──────────────────────────────────────────────────────────────┐
│                     文章串流 (Article Stream)                   │
│                   每小時 6000 篇新文章 ID                         │
└────────────────────┬─────────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────────┐
│              Reaction Bot Service (反應機器人服務)              │
│                                                                │
│  1. 接收文章 ID 列表                                             │
│  2. 計算總反應數 = 文章數 × 反應倍數%                             │
│  3. Poisson 分佈演算法分配反應                                   │
│  4. 從 KOL 池中隨機選擇執行者                                     │
│  5. 發送反應 (帶隨機延遲)                                         │
│  6. 記錄日誌                                                     │
└────────────┬──────────────────────────────┬──────────────────┘
             │                              │
             ▼                              ▼
    ┌────────────────┐            ┌──────────────────┐
    │  CMoney API    │            │  PostgreSQL DB   │
    │  (發送按讚)     │            │  (記錄日誌)        │
    └────────────────┘            └──────────────────┘
             │
             ▼
    ┌────────────────────────────────────────────┐
    │         CMoney 論壇文章                      │
    │         (接收按讚反應)                        │
    └────────────────────────────────────────────┘
```

---

## 核心演算法 - Poisson 分佈

### 為什麼選擇 Poisson 分佈？

Poisson 分佈是描述**稀有事件**發生次數的機率分佈，非常適合模擬自然的按讚行為：

1. **自然隨機性**：大多數文章獲得接近平均值的按讚數
2. **非對稱分佈**：少數文章獲得特別多或特別少的按讚
3. **避免規律性**：不會出現「每篇文章恰好 2 個讚」的可疑模式
4. **符合真實情況**：真實用戶的按讚行為通常遵循 Poisson 分佈

### 演算法實現

```python
class PoissonDistributor:
    def __init__(self, total_articles: int, total_reactions: int):
        self.total_articles = total_articles
        self.total_reactions = total_reactions
        # λ (lambda) = 平均每篇文章的反應數
        self.lambda_param = total_reactions / total_articles

    def distribute(self) -> Dict[int, int]:
        # 使用 numpy 生成 Poisson 分佈
        reactions_per_article = np.random.poisson(
            self.lambda_param,
            self.total_articles
        )

        # 調整至精確總數
        # (Poisson 是隨機的，需要微調以匹配 total_reactions)
        current_total = np.sum(reactions_per_article)
        diff = self.total_reactions - current_total

        # 如果總數不足，隨機增加
        if diff > 0:
            indices = random.sample(range(self.total_articles), diff)
            for idx in indices:
                reactions_per_article[idx] += 1

        # 如果總數過多，隨機減少
        elif diff < 0:
            non_zero_indices = np.where(reactions_per_article > 0)[0]
            indices = random.sample(list(non_zero_indices), abs(diff))
            for idx in indices:
                reactions_per_article[idx] -= 1

        return {i: int(count) for i, count in enumerate(reactions_per_article)}
```

### 分佈範例

**輸入**：
- 1000 篇文章
- 2000 個反應 (200%)
- λ = 2000 / 1000 = 2.0

**輸出 (典型分佈)**：
```
0 個讚: 135 篇 (13.5%)
1 個讚: 271 篇 (27.1%)
2 個讚: 271 篇 (27.1%)  ← 最常見
3 個讚: 180 篇 (18.0%)
4 個讚: 90 篇 (9.0%)
5 個讚: 36 篇 (3.6%)
6+ 個讚: 17 篇 (1.7%)
總計: 1000 篇, 2000 個讚
```

---

## 資料庫結構

### 表格清單

1. **reaction_bot_config** - 機器人配置
2. **reaction_bot_logs** - 反應活動日誌
3. **reaction_bot_batches** - 批次處理記錄
4. **reaction_bot_article_queue** - 文章待處理佇列
5. **reaction_bot_stats** - 每日統計摘要

### 表格結構詳情

#### 1. reaction_bot_config
```sql
CREATE TABLE reaction_bot_config (
    id SERIAL PRIMARY KEY,
    enabled BOOLEAN DEFAULT false,              -- 是否啟用機器人
    reaction_percentage INT DEFAULT 100,        -- 反應倍數 (100 = 1x)
    selected_kol_serials JSON DEFAULT '[]',     -- 選定的 KOL 列表 [201, 202, 203]
    distribution_algorithm VARCHAR(50) DEFAULT 'poisson',  -- 分佈演算法
    min_delay_seconds FLOAT DEFAULT 0.5,        -- 最小延遲
    max_delay_seconds FLOAT DEFAULT 2.0,        -- 最大延遲
    max_reactions_per_kol_per_hour INT DEFAULT 100,  -- 每 KOL 每小時上限
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### 2. reaction_bot_logs
```sql
CREATE TABLE reaction_bot_logs (
    id SERIAL PRIMARY KEY,
    article_id VARCHAR(50) NOT NULL,            -- 文章 ID
    kol_serial INT NOT NULL,                    -- 執行的 KOL
    reaction_type VARCHAR(20) DEFAULT 'like',   -- 反應類型
    success BOOLEAN DEFAULT true,               -- 是否成功
    error_message TEXT,                         -- 錯誤訊息
    response_data JSON,                         -- API 回應
    timestamp TIMESTAMP DEFAULT NOW(),

    INDEX idx_reaction_bot_logs_article_id (article_id),
    INDEX idx_reaction_bot_logs_kol_serial (kol_serial),
    INDEX idx_reaction_bot_logs_timestamp (timestamp DESC)
);
```

#### 3. reaction_bot_batches
```sql
CREATE TABLE reaction_bot_batches (
    id SERIAL PRIMARY KEY,
    batch_id VARCHAR(100) UNIQUE NOT NULL,      -- 批次 ID
    article_count INT DEFAULT 0,                -- 文章數量
    total_reactions INT DEFAULT 0,              -- 總反應數
    reactions_sent INT DEFAULT 0,               -- 已發送
    reactions_failed INT DEFAULT 0,             -- 失敗數
    status VARCHAR(20) DEFAULT 'pending',       -- 狀態
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### 4. reaction_bot_article_queue
```sql
CREATE TABLE reaction_bot_article_queue (
    id SERIAL PRIMARY KEY,
    batch_id VARCHAR(100),
    article_id VARCHAR(50) NOT NULL,            -- 文章 ID
    assigned_reactions INT DEFAULT 0,           -- 分配的反應數
    reactions_sent INT DEFAULT 0,               -- 已發送
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW(),
    processed_at TIMESTAMP,

    CONSTRAINT fk_batch FOREIGN KEY (batch_id)
        REFERENCES reaction_bot_batches(batch_id) ON DELETE CASCADE
);
```

#### 5. reaction_bot_stats
```sql
CREATE TABLE reaction_bot_stats (
    id SERIAL PRIMARY KEY,
    date DATE UNIQUE NOT NULL,                  -- 日期
    total_batches INT DEFAULT 0,                -- 總批次數
    total_articles_processed INT DEFAULT 0,     -- 處理的文章數
    total_reactions_sent INT DEFAULT 0,         -- 發送的反應數
    total_reactions_failed INT DEFAULT 0,       -- 失敗的反應數
    avg_reactions_per_article FLOAT DEFAULT 0.0,  -- 平均每篇反應數
    success_rate FLOAT DEFAULT 0.0,             -- 成功率 (%)
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 後端 API

### API 端點清單

#### 1. GET `/api/reaction-bot/config`
**描述**：獲取當前機器人配置

**回應**：
```json
{
  "enabled": true,
  "reaction_percentage": 200,
  "selected_kol_serials": [201, 202, 203],
  "distribution_algorithm": "poisson",
  "min_delay_seconds": 0.5,
  "max_delay_seconds": 2.0,
  "max_reactions_per_kol_per_hour": 100,
  "created_at": "2025-11-10T10:00:00",
  "updated_at": "2025-11-10T10:00:00"
}
```

#### 2. PUT `/api/reaction-bot/config`
**描述**：更新機器人配置

**請求體**：
```json
{
  "enabled": true,
  "reaction_percentage": 150,
  "selected_kol_serials": [201, 202, 203, 204]
}
```

**回應**：
```json
{
  "success": true,
  "message": "Configuration updated successfully",
  "config": { ... }
}
```

#### 3. POST `/api/reaction-bot/process-batch`
**描述**：處理一批文章 ID，發送反應

**請求體**：
```json
{
  "article_ids": [
    "article_001",
    "article_002",
    "article_003",
    ...
  ],
  "batch_id": "batch_2025-11-10_14-00-00"  // 可選
}
```

**回應**：
```json
{
  "success": true,
  "batch_id": "batch_2025-11-10_14-00-00",
  "reactions_sent": 11850,
  "reactions_failed": 150,
  "total_articles": 6000,
  "total_reactions": 12000
}
```

#### 4. GET `/api/reaction-bot/stats`
**描述**：獲取統計數據

**查詢參數**：
- `days`: 天數 (預設 7, 最大 90)

**回應**：
```json
{
  "daily_stats": [
    {
      "date": "2025-11-10",
      "total_batches": 5,
      "total_articles_processed": 30000,
      "total_reactions_sent": 59500,
      "total_reactions_failed": 500,
      "avg_reactions_per_article": 1.98,
      "success_rate": 99.17
    },
    ...
  ],
  "overall": {
    "total_batches": 35,
    "total_reactions_sent": 415000,
    "total_reactions_failed": 3500,
    "avg_reactions_per_article": 2.01
  },
  "period_days": 7
}
```

#### 5. GET `/api/reaction-bot/logs`
**描述**：獲取活動日誌

**查詢參數**：
- `limit`: 數量限制 (預設 100, 最大 1000)
- `offset`: 分頁偏移 (預設 0)
- `article_id`: 篩選文章 ID
- `kol_serial`: 篩選 KOL
- `success`: 篩選成功狀態 (true/false)

**回應**：
```json
{
  "success": true,
  "logs": [
    {
      "id": 12345,
      "article_id": "article_001",
      "kol_serial": 201,
      "reaction_type": "like",
      "success": true,
      "timestamp": "2025-11-10T14:05:23"
    },
    ...
  ],
  "count": 100,
  "limit": 100,
  "offset": 0
}
```

#### 6. GET `/api/reaction-bot/batches`
**描述**：獲取批次處理記錄

**查詢參數**：
- `limit`: 數量限制 (預設 20, 最大 100)
- `offset`: 分頁偏移 (預設 0)
- `status`: 篩選狀態 (pending/processing/completed/failed)

**回應**：
```json
{
  "success": true,
  "batches": [
    {
      "id": 123,
      "batch_id": "batch_2025-11-10_14-00-00",
      "article_count": 6000,
      "total_reactions": 12000,
      "reactions_sent": 11850,
      "reactions_failed": 150,
      "status": "completed",
      "created_at": "2025-11-10T14:00:00",
      "completed_at": "2025-11-10T14:25:30"
    },
    ...
  ],
  "count": 20
}
```

#### 7. POST `/api/reaction-bot/test-distribution`
**描述**：測試分佈演算法 (不實際發送反應)

**查詢參數**：
- `article_count`: 文章數量 (1-10000)
- `reaction_percentage`: 反應倍數 (1-1000)

**回應**：
```json
{
  "success": true,
  "article_count": 1000,
  "total_reactions": 2000,
  "reaction_percentage": 200,
  "statistics": {
    "zero_reactions": 135,
    "with_reactions": 865,
    "max_reactions": 8,
    "min_reactions": 0,
    "avg_reactions": 2.0
  },
  "histogram": {
    "0": 135,
    "1": 271,
    "2": 271,
    "3": 180,
    "4": 90,
    "5": 36,
    "6": 12,
    "7": 4,
    "8": 1
  },
  "sample_distribution": {
    "article_0": 2,
    "article_1": 1,
    "article_2": 3,
    ...
  }
}
```

---

## 前端 UI

### 頁面位置
**路徑**: `/engagement-management`
**側邊欄**: 互動管理 → (所有子項目都導向同一頁面)

### UI 組件

#### 1. 頂部狀態卡片
```
┌─────────────┬─────────────┬─────────────┬─────────────┐
│ 機器人狀態   │ 總批次       │ 總反應數     │ 成功率       │
│ 運行中 🟢   │ 35          │ 415,000     │ 99.2%       │
│ [啟用切換]   │             │             │             │
└─────────────┴─────────────┴─────────────┴─────────────┘
```

#### 2. 配置面板
```
┌──────────────────────────────────────────────────────────┐
│ ⚙️ 機器人配置                          [保存配置]         │
├──────────────────────────────────────────────────────────┤
│                                                            │
│ 👥 KOL 選擇池                                              │
│ [下拉多選] 川川哥 (#201), 投資達人 (#202), ...             │
│ 已選擇 3 個 KOL                                            │
│                                                            │
│ 📊 反應倍數                                                │
│ [滑桿] ────●────────── 200%                               │
│ 範例：6000 篇文章 × 200% = 12,000 個反應                   │
│                                                            │
│ ⚡ 反應延遲 (秒)                                           │
│ 最小延遲: [0.5] 秒    最大延遲: [2.0] 秒                   │
│                                                            │
│ ℹ️ 每 KOL 每小時反應上限                                   │
│ [100] 個反應                                               │
│                                                            │
│ 📊 分佈演算法                                              │
│ [下拉選單] Poisson 分佈 (推薦)                             │
│                                                            │
│ ⚡ 測試分佈                                                │
│ [測試 Poisson 分佈 (1000 篇文章)]                          │
└──────────────────────────────────────────────────────────┘
```

#### 3. 批次執行記錄表格
```
┌──────────────────────────────────────────────────────────┐
│ ⚡ 批次執行記錄                              [刷新]        │
├──────────────────────────────────────────────────────────┤
│ 批次 ID | 文章數 | 反應總數 | 已發送 | 失敗 | 狀態 | 時間 │
├──────────────────────────────────────────────────────────┤
│ batch_... | 6000 | 12000 | 11850 | 150 | 完成 ✅ | ... │
│ batch_... | 5500 | 11000 | 10890 | 110 | 完成 ✅ | ... │
│ ...                                                        │
└──────────────────────────────────────────────────────────┘
```

#### 4. 活動日誌表格
```
┌──────────────────────────────────────────────────────────┐
│ 📊 活動日誌 (最近 50 筆)                     [刷新]        │
├──────────────────────────────────────────────────────────┤
│ 文章 ID | KOL | 反應類型 | 狀態 | 時間                     │
├──────────────────────────────────────────────────────────┤
│ art_001 | 川川哥 | like | ✅ 成功 | 2025-11-10 14:05:23 │
│ art_002 | 投資達人 | like | ✅ 成功 | 2025-11-10 14:05:24 │
│ ...                                                        │
└──────────────────────────────────────────────────────────┘
```

#### 5. 測試分佈彈窗
```
┌──────────────────────────────────────────────┐
│ Poisson 分佈測試結果                    [關閉] │
├──────────────────────────────────────────────┤
│ 文章總數: 1000   反應總數: 2000   倍數: 200% │
│                                                │
│ 統計數據：                                     │
│ • 零反應文章: 135                              │
│ • 有反應文章: 865                              │
│ • 最大反應數: 8                                │
│ • 平均反應數: 2.0                              │
│                                                │
│ 反應數分佈直方圖：                             │
│ 0 個反應: ████████████░░░░░░ 135 篇 (13.5%) │
│ 1 個反應: ████████████████████ 271 篇 (27.1%)│
│ 2 個反應: ████████████████████ 271 篇 (27.1%)│
│ 3 個反應: ██████████████░░░░░ 180 篇 (18.0%)│
│ 4 個反應: ███████░░░░░░░░░░░░ 90 篇 (9.0%)  │
│ ...                                            │
└──────────────────────────────────────────────┘
```

---

## 使用流程

### 初次設定

1. **執行資料庫遷移**
   ```bash
   psql -U postgres -d posting_management -f migrations/add_reaction_bot_tables.sql
   ```

2. **啟動後端服務**
   ```bash
   cd docker-container/finlab\ python/apps/unified-api
   python main.py
   ```

3. **啟動前端**
   ```bash
   cd docker-container/finlab\ python/apps/dashboard-frontend
   npm run dev
   ```

4. **開啟互動管理頁面**
   - 導航至: http://localhost:3000/engagement-management

### 日常使用

1. **選擇 KOL 池**
   - 在「KOL 選擇池」下拉選單中選擇要使用的 KOL 帳號
   - 建議選擇 3-5 個 KOL 以分散負載

2. **設定反應倍數**
   - 使用滑桿或輸入框設定反應倍數
   - 100% = 與文章數相同的反應數
   - 200% = 文章數的 2 倍反應數

3. **測試分佈 (可選)**
   - 點擊「測試 Poisson 分佈」按鈕
   - 查看模擬結果，確保分佈符合預期

4. **保存配置**
   - 點擊「保存配置」按鈕

5. **啟用機器人**
   - 切換「機器人狀態」開關至「啟用」

6. **發送文章批次**
   - (待實現) 當有新文章串流時，系統自動調用 `/api/reaction-bot/process-batch`
   - 或手動調用 API 測試：
   ```bash
   curl -X POST http://localhost:8001/api/reaction-bot/process-batch \
     -H "Content-Type: application/json" \
     -d '{
       "article_ids": ["art_001", "art_002", ..., "art_6000"]
     }'
   ```

7. **監控執行**
   - 在「批次執行記錄」表格中查看處理進度
   - 在「活動日誌」中查看詳細反應記錄

---

## 部署指南

### 前置需求

1. **Python 依賴**
   ```bash
   pip install numpy asyncpg fastapi pydantic
   ```

2. **資料庫**
   - PostgreSQL 15+
   - 資料庫名稱: `posting_management`

3. **環境變數**
   ```bash
   DATABASE_URL=postgresql://user:password@localhost:5432/posting_management
   CMONEY_API_URL=https://api.cmoney.com
   CMONEY_API_KEY=your_api_key
   ```

### 部署步驟

#### 1. 部署資料庫
```bash
# 連接資料庫
psql -U postgres -d posting_management

# 執行遷移
\i /path/to/add_reaction_bot_tables.sql

# 驗證表格
\dt reaction_bot*
```

#### 2. 部署後端
```bash
# 複製檔案至 unified-api
cp reaction_bot_service.py docker-container/finlab\ python/apps/unified-api/
cp reaction_bot_routes.py docker-container/finlab\ python/apps/unified-api/

# 在 main.py 中註冊路由
# 加入以下程式碼:
from reaction_bot_routes import router as reaction_bot_router
app.include_router(reaction_bot_router)

# 重啟服務
systemctl restart unified-api
# 或
docker-compose restart unified-api
```

#### 3. 部署前端
```bash
# 複製 UI 檔案
cp EngagementManagementPage.tsx docker-container/finlab\ python/apps/dashboard-frontend/src/pages/

# 已在 App.tsx 中添加路由 (本次部署已完成)

# 重新構建
npm run build

# 部署至 Vercel/Netlify
vercel deploy
# 或
netlify deploy --prod
```

#### 4. 測試端點
```bash
# 測試配置端點
curl http://localhost:8001/api/reaction-bot/config

# 測試分佈演算法
curl "http://localhost:8001/api/reaction-bot/test-distribution?article_count=1000&reaction_percentage=200"

# 健康檢查
curl http://localhost:8001/api/reaction-bot/health
```

---

## 測試計畫

### 單元測試

#### 1. Poisson 分佈測試
```python
def test_poisson_distribution():
    distributor = PoissonDistributor(1000, 2000)
    distribution = distributor.distribute()

    # 驗證總數正確
    assert sum(distribution.values()) == 2000

    # 驗證文章數正確
    assert len(distribution) == 1000

    # 驗證有零反應文章
    zero_count = sum(1 for count in distribution.values() if count == 0)
    assert zero_count > 0

    # 驗證平均值接近 2.0
    avg = sum(distribution.values()) / len(distribution)
    assert 1.8 <= avg <= 2.2
```

#### 2. API 端點測試
```python
async def test_get_config():
    response = await client.get("/api/reaction-bot/config")
    assert response.status_code == 200
    data = response.json()
    assert "enabled" in data
    assert "reaction_percentage" in data

async def test_update_config():
    response = await client.put(
        "/api/reaction-bot/config",
        json={"reaction_percentage": 150}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
```

### 整合測試

#### 1. 完整流程測試
```python
async def test_full_workflow():
    # 1. 更新配置
    await client.put("/api/reaction-bot/config", json={
        "enabled": True,
        "reaction_percentage": 200,
        "selected_kol_serials": [201, 202, 203]
    })

    # 2. 處理批次
    article_ids = [f"art_{i:04d}" for i in range(100)]
    response = await client.post(
        "/api/reaction-bot/process-batch",
        json={"article_ids": article_ids}
    )
    assert response.status_code == 200
    result = response.json()

    # 3. 驗證結果
    assert result["reactions_sent"] > 0
    assert result["total_articles"] == 100

    # 4. 檢查日誌
    logs_response = await client.get("/api/reaction-bot/logs?limit=10")
    logs = logs_response.json()["logs"]
    assert len(logs) > 0
```

### 壓力測試

#### 1. 大批次測試
```python
async def test_large_batch():
    # 測試 10,000 篇文章
    article_ids = [f"art_{i:06d}" for i in range(10000)]

    start_time = time.time()
    response = await client.post(
        "/api/reaction-bot/process-batch",
        json={"article_ids": article_ids}
    )
    end_time = time.time()

    # 驗證在合理時間內完成 (假設每個反應 1 秒，共 20,000 秒)
    duration = end_time - start_time
    assert duration < 25000  # 允許 25% 容錯

    result = response.json()
    assert result["reactions_sent"] > 15000  # 至少 75% 成功
```

---

## 待辦事項

### 🔴 關鍵 (立即處理)

1. **整合 CMoney API**
   - [ ] 在 `reaction_bot_service.py` 的 `_send_reaction()` 方法中整合真實的 CMoney API
   - [ ] 測試 API 回應格式
   - [ ] 處理錯誤情況 (API 限流、認證失敗等)

2. **實現文章串流數據接口**
   - [ ] 與您討論文章串流數據來源
   - [ ] 實現 `/api/article-stream/latest` 端點
   - [ ] 實現定時任務，每小時自動獲取新文章 ID
   - [ ] 自動觸發 reaction bot 處理

3. **資料庫遷移執行**
   - [ ] 在正式環境執行 `add_reaction_bot_tables.sql`
   - [ ] 驗證所有表格和索引

4. **後端路由註冊**
   - [ ] 在 unified-API 的 `main.py` 中引入並註冊 `reaction_bot_routes`
   ```python
   from reaction_bot_routes import router as reaction_bot_router
   app.include_router(reaction_bot_router)
   ```

### 🟡 重要 (近期處理)

5. **KOL 憑證管理**
   - [ ] 實現 KOL 憑證存儲 (用戶名、密碼、token)
   - [ ] 在發送反應前自動登入 KOL 帳號
   - [ ] Token 過期自動重新登入

6. **錯誤處理增強**
   - [ ] 實現重試機制 (失敗自動重試 3 次)
   - [ ] 實現降級策略 (部分 KOL 失敗時繼續其他 KOL)
   - [ ] 詳細錯誤分類 (API 錯誤、網路錯誤、認證錯誤等)

7. **監控和告警**
   - [ ] 實現實時監控儀表板
   - [ ] 失敗率過高時發送告警
   - [ ] 每日統計報告自動生成

8. **前端功能完善**
   - [ ] 實現手動觸發批次處理按鈕
   - [ ] 實現暫停/恢復批次處理
   - [ ] 實現即時進度條顯示

### 🟢 優化 (後續改進)

9. **性能優化**
   - [ ] 實現批次並發處理 (asyncio.gather)
   - [ ] 資料庫連接池優化
   - [ ] 快取 KOL 憑證

10. **功能擴展**
    - [ ] 支援其他反應類型 (分享、收藏、留言)
    - [ ] 智能時段分配 (高峰時段減少反應速率)
    - [ ] A/B 測試不同分佈演算法

11. **文件和培訓**
    - [ ] 編寫用戶操作手冊
    - [ ] 錄製操作教學影片
    - [ ] 編寫 API 使用範例

12. **安全性增強**
    - [ ] API 認證和授權
    - [ ] 速率限制 (防止濫用)
    - [ ] 敏感數據加密

---

## 附錄

### A. CMoney API 整合指南

**待您提供**：
1. CMoney 按讚 API 端點
2. 請求格式和參數
3. 認證方式 (Bearer token / API key)
4. 回應格式

**預期整合位置**：
- 檔案: `reaction_bot_service.py`
- 方法: `_send_reaction()`
- 程式碼範例：
```python
async def _send_reaction(self, article_id: str, kol_serial: int) -> Tuple[bool, Dict]:
    try:
        # 獲取 KOL 憑證
        kol_credentials = await self._get_kol_credentials(kol_serial)

        # 呼叫 CMoney API
        response = await self.cmoney_client.send_reaction(
            article_id=article_id,
            user_token=kol_credentials['token'],
            reaction_type='like'
        )

        if response.status_code == 200:
            return True, response.json()
        else:
            return False, {"error": response.text}

    except Exception as e:
        logger.error(f"❌ CMoney API error: {e}")
        return False, {"error": str(e)}
```

### B. 文章串流整合指南

**待您提供**：
1. 文章串流數據來源 (API 端點 / 資料庫查詢 / Kafka topic)
2. 資料格式
3. 更新頻率 (每小時 / 即時)

**預期整合方式**：
```python
# 定時任務 (每小時執行)
from apscheduler.schedulers.asyncio import AsyncIOScheduler

async def fetch_and_process_articles():
    # 1. 獲取最新文章 ID
    article_ids = await fetch_latest_article_ids()

    # 2. 自動觸發 reaction bot
    if article_ids:
        await reaction_bot_service.process_article_batch(article_ids)

scheduler = AsyncIOScheduler()
scheduler.add_job(fetch_and_process_articles, 'cron', hour='*')  # 每小時
scheduler.start()
```

### C. 檔案清單

**後端檔案**：
- `docker-container/finlab python/apps/unified-api/migrations/add_reaction_bot_tables.sql` ✅
- `docker-container/finlab python/apps/unified-api/reaction_bot_service.py` ✅
- `docker-container/finlab python/apps/unified-api/reaction_bot_routes.py` ✅

**前端檔案**：
- `docker-container/finlab python/apps/dashboard-frontend/src/pages/EngagementManagementPage.tsx` ✅
- `docker-container/finlab python/apps/dashboard-frontend/src/App.tsx` (已修改) ✅

**文件檔案**：
- `REACTION_BOT_DOCUMENTATION.md` ✅

---

## 總結

✅ **已完成**：
1. 完整的資料庫結構設計 (5 個表格)
2. Poisson 分佈演算法實現
3. 完整的後端 API (8 個端點)
4. 全功能前端 UI (單頁面整合所有設定)
5. 路由配置 (Sidebar + App.tsx)
6. 詳細技術文件

⏳ **待完成**：
1. CMoney API 整合 (需要您提供 API 資訊)
2. 文章串流數據接口 (需要您提供資料來源)
3. 資料庫遷移執行
4. 後端路由註冊
5. KOL 憑證管理

📞 **下一步**：
請提供以下資訊，我可以立即整合：
1. CMoney 按讚 API 的端點、請求格式、認證方式
2. 文章串流數據的來源和格式

**本功能已準備好部署測試！** 🚀

---

**文件版本**: 1.0
**最後更新**: 2025-11-10
**作者**: Claude Code
