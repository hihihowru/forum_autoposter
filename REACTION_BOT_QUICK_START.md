# 自動按讚機器人 - 快速開始指南

## 🎯 核心概念 (5 秒理解)

**功能**: 自動隨機分配按讚給新文章
**輸入**: 6000 篇文章 ID
**設定**: 200% 反應倍數 = 12,000 個讚
**演算法**: Poisson 分佈 (部分文章 0 讚, 部分 1-2 讚, 少數 3+ 讚)
**執行**: 從 KOL 池中隨機選擇帳號發送

---

## 🚀 快速啟動 (3 步驟)

### 1. 執行資料庫遷移
```bash
psql -U postgres -d posting_management -f "docker-container/finlab python/apps/unified-api/migrations/add_reaction_bot_tables.sql"
```

### 2. 註冊後端路由
在 `unified-api/main.py` 加入:
```python
from reaction_bot_routes import router as reaction_bot_router
app.include_router(reaction_bot_router)
```

### 3. 重啟服務
```bash
# Backend
docker-compose restart unified-api

# Frontend (如已部署)
npm run build && vercel deploy
```

**完成！** 🎉 現在可以在 `/engagement-management` 使用功能

---

## 📋 檔案清單

### 後端
✅ `unified-api/migrations/add_reaction_bot_tables.sql` - 資料庫遷移
✅ `unified-api/reaction_bot_service.py` - 核心服務 (Poisson 分佈)
✅ `unified-api/reaction_bot_routes.py` - API 端點

### 前端
✅ `dashboard-frontend/src/pages/EngagementManagementPage.tsx` - UI 頁面
✅ `dashboard-frontend/src/App.tsx` - 路由 (已修改)

### 文件
✅ `REACTION_BOT_DOCUMENTATION.md` - 完整文件
✅ `REACTION_BOT_QUICK_START.md` - 本檔案

---

## 🔧 待完成項目

### 🔴 立即需要
1. **CMoney API 整合** - 需要您提供 API 資訊
2. **文章串流數據** - 需要您提供資料來源

### 程式碼位置
- **CMoney API**: `reaction_bot_service.py:_send_reaction()` (第 ~250 行)
- **文章串流**: 建立新端點或定時任務

---

## 📞 提供資訊後可立即整合

### 1. CMoney API 資訊
請提供:
```
端點: POST https://api.cmoney.com/...?
參數: { article_id, user_id, action: "like" }
認證: Bearer token / API key
回應: { success: true, ... }
```

### 2. 文章串流資訊
請提供:
```
來源: API / 資料庫 / Kafka
端點: GET https://...
格式: ["art_001", "art_002", ...]
頻率: 每小時 / 即時
```

---

## 🧪 測試 API (本地)

```bash
# 1. 測試配置端點
curl http://localhost:8001/api/reaction-bot/config

# 2. 測試分佈演算法
curl "http://localhost:8001/api/reaction-bot/test-distribution?article_count=1000&reaction_percentage=200"

# 3. 模擬處理批次 (使用模擬資料)
curl -X POST http://localhost:8001/api/reaction-bot/process-batch \
  -H "Content-Type: application/json" \
  -d '{
    "article_ids": ["art_001", "art_002", "art_003"]
  }'

# 4. 查看日誌
curl http://localhost:8001/api/reaction-bot/logs?limit=10

# 5. 查看統計
curl http://localhost:8001/api/reaction-bot/stats?days=7
```

---

## 🎨 UI 預覽

前往: `http://localhost:3000/engagement-management`

**功能**:
- ✅ 啟用/停用機器人
- ✅ 選擇 KOL 池 (多選下拉)
- ✅ 設定反應倍數 (滑桿 + 輸入框)
- ✅ 設定延遲時間
- ✅ 測試 Poisson 分佈
- ✅ 查看批次記錄
- ✅ 查看活動日誌
- ✅ 即時統計數據

---

## 🐛 常見問題

### Q1: 404 Not Found - /api/reaction-bot/config
**A**: 後端路由未註冊，檢查 `main.py` 是否加入 `reaction_bot_router`

### Q2: 資料庫表格不存在
**A**: 執行資料庫遷移 SQL 檔案

### Q3: Frontend 找不到 EngagementManagementPage
**A**: 檔案路徑確認: `src/pages/EngagementManagementPage.tsx`

### Q4: Poisson 分佈計算錯誤
**A**: 確認已安裝 `numpy`: `pip install numpy`

---

## 📊 Poisson 分佈範例

**輸入**: 1000 篇文章, 2000 個反應 (200%)

**輸出**:
```
0 讚: 135 篇 (13.5%)
1 讚: 271 篇 (27.1%)
2 讚: 271 篇 (27.1%) ← 最常見
3 讚: 180 篇 (18.0%)
4 讚: 90 篇 (9.0%)
5+ 讚: 53 篇 (5.3%)
```

**特點**:
- 自然隨機分佈
- 模擬真實用戶行為
- 避免過於規律 (不會每篇都恰好 2 讚)

---

## ✅ 檢查清單

部署前確認:

Backend:
- [ ] 資料庫遷移已執行
- [ ] reaction_bot_service.py 已複製
- [ ] reaction_bot_routes.py 已複製
- [ ] main.py 已註冊路由
- [ ] numpy 已安裝
- [ ] 服務已重啟

Frontend:
- [ ] EngagementManagementPage.tsx 已複製
- [ ] App.tsx 已更新 (import + routes)
- [ ] 已重新構建
- [ ] 已部署至 Vercel/Netlify

測試:
- [ ] GET /api/reaction-bot/config 返回 200
- [ ] GET /api/reaction-bot/health 返回 healthy
- [ ] UI 頁面可正常載入
- [ ] KOL 列表可正常顯示
- [ ] 測試分佈功能正常

---

## 🚀 準備就緒！

**目前狀態**: 80% 完成
**剩餘工作**: CMoney API + 文章串流整合
**預計時間**: 提供資訊後 1-2 小時

**下一步**:
請提供 CMoney API 和文章串流資訊，我將立即完成整合！

---

**快速聯繫**: 需要協助請提供問題描述 + 錯誤訊息 + 操作步驟
