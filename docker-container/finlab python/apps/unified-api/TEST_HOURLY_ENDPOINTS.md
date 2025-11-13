# Hourly Reaction Service - API 測試指南

## 🚀 新增的 API Endpoints

### 1. 手動執行每小時任務
```bash
POST /api/reaction-bot/hourly-task/run
```

**功能：**
- 抓取過去 1 小時的文章（Kafka 即時資料流）
- 使用 KOL 池子按讚（自動輪換）
- 儲存統計到 `hourly_reaction_stats` 資料表

**測試指令：**
```bash
# 使用所有活躍的 KOL
curl -X POST "https://your-domain/api/reaction-bot/hourly-task/run"

# 指定特定 KOL serials
curl -X POST "https://your-domain/api/reaction-bot/hourly-task/run" \
  -H "Content-Type: application/json" \
  -d '{"kol_serials": [1, 2, 3]}'
```

---

### 2. 查看每小時統計（列表）
```bash
GET /api/reaction-bot/hourly-stats?limit=24&offset=0
```

**功能：**
- 查看最近的每小時統計記錄
- 支援分頁

**測試指令：**
```bash
# 查看最近 24 筆記錄
curl "https://your-domain/api/reaction-bot/hourly-stats?limit=24&offset=0"
```

**回傳範例：**
```json
{
  "success": true,
  "stats": [
    {
      "id": 1,
      "hour_start": "2025-11-13T12:00:00",
      "hour_end": "2025-11-13T13:00:00",
      "total_new_articles": 2462,
      "total_like_attempts": 2462,
      "successful_likes": 2450,
      "unique_articles_liked": 2450,
      "like_success_rate": 99.51,
      "kol_pool_serials": [1, 2, 3, 4, 5],
      "created_at": "2025-11-13T13:05:00",
      "updated_at": "2025-11-13T13:05:00"
    }
  ],
  "count": 1,
  "total_count": 1,
  "limit": 24,
  "offset": 0
}
```

---

### 3. 查看最新統計
```bash
GET /api/reaction-bot/hourly-stats/latest
```

**功能：**
- 快速查看最新一筆統計記錄
- 包含文章 ID 樣本

**測試指令：**
```bash
curl "https://your-domain/api/reaction-bot/hourly-stats/latest"
```

---

### 4. 查看統計摘要
```bash
GET /api/reaction-bot/hourly-stats/summary?hours=24
```

**功能：**
- 聚合統計過去 N 小時的資料
- 計算平均值、總計等

**測試指令：**
```bash
# 查看過去 24 小時的摘要
curl "https://your-domain/api/reaction-bot/hourly-stats/summary?hours=24"
```

**回傳範例：**
```json
{
  "success": true,
  "summary": {
    "hours_analyzed": 24,
    "total_hours_with_data": 3,
    "total_new_articles": 7500,
    "total_like_attempts": 7500,
    "total_successful_likes": 7450,
    "total_unique_articles_liked": 7450,
    "average_success_rate": 99.33,
    "earliest_hour": "2025-11-13T10:00:00",
    "latest_hour": "2025-11-13T12:00:00",
    "articles_per_hour": 2500.0,
    "likes_per_hour": 2483.33
  }
}
```

---

## 📊 測試流程建議

### Step 1: 確認資料表已建立
```bash
# 檢查 Railway logs 確認資料表是否建立成功
```

### Step 2: 手動執行一次每小時任務
```bash
curl -X POST "https://forum-autoposter-backend-production.up.railway.app/api/reaction-bot/hourly-task/run"
```

### Step 3: 查看最新統計
```bash
curl "https://forum-autoposter-backend-production.up.railway.app/api/reaction-bot/hourly-stats/latest"
```

### Step 4: 查看統計摘要
```bash
curl "https://forum-autoposter-backend-production.up.railway.app/api/reaction-bot/hourly-stats/summary?hours=24"
```

---

## 🔍 預期結果

### 如果一切正常，你會看到：

1. **手動執行任務：**
   - ✅ `success: true`
   - ✅ 抓到 2000+ 篇文章
   - ✅ 按讚成功率 > 95%

2. **查看統計：**
   - ✅ 有完整的統計記錄
   - ✅ 包含 KOL serials
   - ✅ 顯示成功率

3. **統計摘要：**
   - ✅ 顯示總計和平均值
   - ✅ 每小時平均文章數約 2000+
   - ✅ 每小時平均按讚數約 2000+

---

## 🐛 常見問題排查

### 問題 1: 資料表不存在
**錯誤：** `relation "hourly_reaction_stats" does not exist`

**解決方法：**
1. 檢查 `migrations/create_hourly_reaction_stats.sql` 是否存在
2. Railway 重新部署後會自動建立

### 問題 2: KOL 登入失敗
**錯誤：** `Failed to login KOL`

**解決方法：**
1. 檢查 `kol_profiles` 資料表是否有活躍的 KOL
2. 確認 KOL 的 email/password 正確

### 問題 3: 文章抓取為空
**錯誤：** `No articles found`

**解決方法：**
- 這是正常的！如果當前小時沒有新文章，就會是 0
- 可以測試過去 3 小時：修改 `hours_back` 參數

---

## 📝 資料表結構

```sql
CREATE TABLE hourly_reaction_stats (
    id SERIAL PRIMARY KEY,
    hour_start TIMESTAMP NOT NULL,
    hour_end TIMESTAMP NOT NULL,
    total_new_articles INT DEFAULT 0,
    total_like_attempts INT DEFAULT 0,
    successful_likes INT DEFAULT 0,
    unique_articles_liked INT DEFAULT 0,
    like_success_rate DECIMAL(5, 2) DEFAULT 0.00,
    kol_pool_serials INT[] DEFAULT '{}',
    article_ids TEXT[] DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(hour_start)
);
```

---

## 🎯 下一步

1. ✅ 測試所有 API endpoints
2. ⏰ 設定 cronjob 每小時自動執行
3. 📊 建立前端 UI 顯示統計圖表
4. 🎨 實作 KOL pool 選擇介面（drag/multi-select）
