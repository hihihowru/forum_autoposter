# ✅ Hourly Reaction Service - 準備測試！

## 🎉 已完成功能

### 1. **Kafka 即時資料流整合** ✅
- 從 `ext_create_article_message` 抓取即時文章
- 自動過濾已刪除的文章
- 測試結果：過去 1 小時 **2,462 篇文章**

### 2. **KOL 輪換按讚系統** ✅
- 自動登入 KOL 並取得 token
- 每個 KOL 按讚 X 篇後自動切換
- 避免重複登入（token caching）

### 3. **每小時統計記錄** ✅
- 儲存到 `hourly_reaction_stats` 資料表
- 記錄文章數、按讚數、成功率
- 記錄使用的 KOL serials 和 article IDs

### 4. **API Endpoints** ✅
- `POST /api/reaction-bot/hourly-task/run` - 手動執行任務
- `GET /api/reaction-bot/hourly-stats` - 查看統計列表
- `GET /api/reaction-bot/hourly-stats/latest` - 最新統計
- `GET /api/reaction-bot/hourly-stats/summary` - 統計摘要

---

## 🧪 快速測試指令

### 方法 1: 使用自動化測試腳本（推薦）
```bash
cd "/Users/willchen/Documents/autoposter/forum_autoposter/docker-container/finlab python/apps/unified-api"
./test_hourly_api.sh
```

### 方法 2: 手動測試關鍵 endpoints

#### 1. 檢查服務健康狀態
```bash
curl https://forum-autoposter-backend-production.up.railway.app/api/reaction-bot/health
```

#### 2. 測試文章抓取（確認 Kafka 資料可用）
```bash
curl "https://forum-autoposter-backend-production.up.railway.app/api/reaction-bot/fetch-articles?hours_back=1"
```
**預期結果：** 應該看到 2000+ 篇文章

#### 3. 手動執行每小時任務（重點！）
```bash
curl -X POST "https://forum-autoposter-backend-production.up.railway.app/api/reaction-bot/hourly-task/run"
```
**注意：** 這個任務會執行 5-10 分鐘（取決於文章數量和 KOL 數量）

#### 4. 查看最新統計
```bash
curl "https://forum-autoposter-backend-production.up.railway.app/api/reaction-bot/hourly-stats/latest"
```

#### 5. 查看統計摘要
```bash
curl "https://forum-autoposter-backend-production.up.railway.app/api/reaction-bot/hourly-stats/summary?hours=24"
```

---

## 📊 預期測試結果

### 成功指標：
- ✅ 文章抓取成功：2000+ 篇/小時
- ✅ 按讚成功率：> 95%
- ✅ KOL 輪換正常：每個 KOL 按讚約 10 篇後切換
- ✅ 統計正確記錄：資料表有完整記錄

### 如果看到以下結果表示正常：
```json
{
  "success": true,
  "stats": {
    "total_new_articles": 2462,
    "total_like_attempts": 2462,
    "successful_likes": 2450,
    "unique_articles_liked": 2450,
    "like_success_rate": 99.51,
    "kol_pool_serials": [1, 2, 3, 4, 5]
  }
}
```

---

## 📁 相關檔案

### 核心邏輯
- `cmoney_article_fetcher.py` - Kafka 資料流查詢
- `hourly_reaction_service.py` - 每小時任務服務
- `cmoney_reaction_client.py` - CMoney 按讚 API 客戶端

### API 路由
- `reaction_bot_routes.py` - 所有 API endpoints

### 資料表 Schema
- `migrations/create_hourly_reaction_stats.sql`

### 測試文件
- `TEST_HOURLY_ENDPOINTS.md` - 完整 API 文檔
- `test_hourly_api.sh` - 自動化測試腳本
- `READY_FOR_TESTING.md` - 本檔案

---

## 🐛 常見問題

### Q1: 資料表不存在？
**A:** Railway 重新部署後會自動建立，如果沒有請檢查 logs

### Q2: KOL 登入失敗？
**A:** 檢查 `kol_profiles` 資料表是否有活躍的 KOL

### Q3: 文章數量為 0？
**A:** 可能當前小時沒有新文章，這是正常的

### Q4: 任務執行太久？
**A:** 2000+ 篇文章 × 2 秒延遲 = 約 1 小時，可以調整 `articles_per_kol` 參數

---

## 🎯 下一步計畫

### Phase 1.5 - 優化（選做）
- [ ] 調整 KOL 輪換策略（articles_per_kol）
- [ ] 調整延遲時間（避免 rate limit）
- [ ] 新增錯誤重試機制

### Phase 2 - Cronjob（重要）
- [ ] 設定每小時自動執行
- [ ] 監控任務執行狀態
- [ ] 錯誤告警機制

### Phase 3 - UI（前端）
- [ ] 統計圖表顯示
- [ ] KOL pool 選擇介面（drag/multi-select）
- [ ] 即時監控 dashboard

---

## 📞 需要協助？

如果測試遇到問題：
1. 查看 Railway deployment logs
2. 檢查 `TEST_HOURLY_ENDPOINTS.md` 的故障排除指南
3. 運行 `./test_hourly_api.sh` 自動化測試

---

**祝測試順利！🚀**

最後更新：2025-11-13
