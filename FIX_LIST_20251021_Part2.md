# 待修復問題清單 - 2025/10/21 Part 2

## 問題1: 前端顯示0篇貼文但後端有1篇 ❌

**症狀**:
- 後端日誌: `✅ 查詢到 1 條貼文數據，總數: 1`
- 前端日誌: `📊 設置貼文數據: 0 篇貼文`
- console.log: `🔍 後端響應數據: Object`, `Array(0)`

**可能原因**:
- API響應數據格式不匹配
- response.data.posts 可能是 undefined 或結構不同

**檢查位置**:
- Backend: `/api/posts` 端點返回格式
- Frontend: `postingManagementAPI.ts:623-650`

**修復方案**: 檢查並修正API響應格式

---

## 問題2: Console.log 顯示無意義訊息 ❌

**症狀**:
```
Session 沒有找到 trigger_type 信息，返回 unknown
```

**修復方案**: 找到並移除或改為調試模式

---

## 問題3: 觸發器類型缺少中文名稱 ❌

**症狀**:
- 顯示 `intraday_volume_leader` (英文)
- 應該顯示中文名稱

**需要的13個觸發器中文名稱**:
1. `trending_topics` → CMoney熱門話題
2. `limit_up_after_hours` → 盤後漲停
3. `limit_down_after_hours` → 盤後跌停
4. `after_hours_volume_amount_high` → 盤後量(金額)大
5. `after_hours_volume_amount_low` → 盤後量(金額)小
6. `after_hours_volume_change_rate_high` → 盤後量增(比率)高
7. `after_hours_volume_change_rate_low` → 盤後量增(比率)低
8. `intraday_limit_up` → 盤中漲停
9. `intraday_limit_down` → 盤中跌停
10. `intraday_limit_up_by_amount` → 盤中漲(金額)
11. `intraday_limit_down_by_amount` → 盤中跌(金額)
12. `intraday_volume_leaders` → 盤中量(成交量)大 ⚠️ **缺少**
13. `intraday_amount_leaders` → 盤中量(金額)大 ⚠️ **缺少**

**修復位置**:
- `ScheduleManagementPage.tsx` triggerTypeMap (line ~587-597)

---

## 問題4: 發文時間顯示"未設定" ❌

**症狀**:
- 用戶設定排程時間為 16:29 或 16:30
- 創建時間 ✅ 正確
- 下次執行時間 ✅ 正確
- **發文時間** ❌ 顯示"開始：未設定"

**原因**:
- `daily_execution_time` 沒有正確從創建排程時傳遞到數據庫
- 或者沒有正確從 API 響應解析

**檢查位置**:
1. 前端創建排程: `BatchScheduleModal.tsx:192` - daily_execution_time
2. 後端存儲: 檢查 schedule_tasks 表是否正確存儲
3. 前端顯示: `ScheduleManagementPage.tsx:612-633`

---

## 問題5: 股票設定"最多 xx 檔"錯誤 ❌

**症狀**:
- 顯示錯誤的最大股票數
- 應該從批次配置獲取

**正確來源**:
- From: `generation_config.triggers.stockCountLimit`
- Or: `generation_config.max_stocks`

**字段來源** (在 TriggerSelector):
- 股票篇數限制: 20 篇
- 篩選依據: 選擇篩選條件

**修復位置**:
- `ScheduleManagementPage.tsx:293` transformApiTask 函數
- 正確解析 `stockCountLimit` from `generation_config`

---

## 修復順序

1. [P0] 問題1: 前端無法顯示貼文 - 影響核心功能
2. [P1] 問題4: 發文時間顯示錯誤 - 用戶已設定但看不到
3. [P1] 問題5: 股票設定顯示錯誤 - 數據不準確
4. [P2] 問題3: 觸發器中文名稱 - UI改進
5. [P3] 問題2: 移除console.log - 清理代碼
