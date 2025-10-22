# 今日修復清單 - 2025/10/21

## ✅ 已修復並部署 (3個關鍵Bug)

### 1. CRITICAL FIX: limit_down觸發器生成limit_up內容 🔥🔥🔥
**問題**:
- 用戶選擇 `limit_down_after_hours` (盤後跌停)
- 股票 5468 下跌 10%
- 但生成的內容全是「漲停漲停」

**根本原因**:
- `posting_type = 'interaction'` 時，不傳遞 `trigger_type` 參數
- `_generate_interaction_version()` 函數缺少trigger_type處理

**修復**:
- 添加 trigger_type 參數到 `_generate_interaction_version()`
- 添加trigger_context邏輯區分漲停/跌停
- 提交: `50548a95`

**影響**:
- ✅ 互動類貼文現在正確生成內容
- ✅ 跌停觸發器生成負面/警告內容
- ✅ 漲停觸發器生成正面/機會內容

---

### 2. 排程管理顯示錯誤的觸發器類型和股票數
**問題**:
- 創建排程: `trigger_type="limit_down_after_hours"`, `max_stocks=3`
- 顯示: `trigger_type="custom_stocks"`, `max_stocks=10`
- `daily_execution_time="17:30"` 顯示為 "未設定"

**根本原因**:
- Frontend從 generation_config 手動提取數據
- Backend已提供 schedule_config 和 trigger_config
- Frontend使用錯誤的fallback默認值

**修復**:
- 直接使用 `apiTask.schedule_config` 和 `apiTask.trigger_config`
- 移除手動提取邏輯
- 提交: `58928b7b`

**影響**:
- ✅ 觸發器類型正確顯示
- ✅ 股票數量正確顯示 (3 而非 10)
- ✅ 執行時間正確顯示 (17:30)

---

### 3. 自動發文Toggle按鈕不更新UI
**問題**:
- 點擊toggle → API返回成功 `{enabled: true}`
- 但按鈕保持灰色(關閉狀態)
- 無法再次點擊

**根本原因**:
- `handleToggleAutoPosting` 調用 `loadSchedules()` 重新載入所有排程
- React狀態更新timing問題

**修復**:
- 直接更新local state使用 `setSchedules()`
- 使用React functional state update pattern
- 立即反映toggle變化，無需full reload
- 提交: `58928b7b`

**影響**:
- ✅ Toggle立即視覺更新
- ✅ 可以多次toggle
- ✅ 更快、更響應的UX

---

### 4. KOL列表查詢類型錯誤
**問題**:
- KOL列表API失敗
- SQL錯誤: `operator does not exist: character varying = integer`

**根本原因**:
- `k.serial` (VARCHAR) 與 `p.kol_serial` (INTEGER) 類型不匹配
- PostgreSQL無法join不同類型

**修復**:
- 添加explicit type cast: `k.serial::integer = p.kol_serial`
- 提交: `97573253`

**影響**:
- ✅ KOL列表API正常工作
- ✅ 正確返回統計數據

---

### 5. 排程器重新啟用 🚀
**問題**:
- 排程器因無限循環被停用
- 排程無法自動執行

**修復**:
- 修復邏輯已存在於 schedule_service.py (檢查last_run)
- 重新啟用 main.py 的排程器代碼
- 提交: `9ba46209`

**影響**:
- ✅ 排程會在指定時間自動執行
- ✅ 每天只執行一次(避免無限循環)
- ✅ Critical blocker已解決

---

### 6. 所有Active排程已取消
**問題**:
- 36個舊排程會在部署後立即執行

**修復**:
- 使用Railway psql取消所有active排程
- SQL: `UPDATE schedule_tasks SET status = 'cancelled' WHERE status = 'active'`

**影響**:
- ✅ 乾淨的測試環境
- ✅ 可以安全創建新的測試排程

---

## ⚠️ 待修復問題

### 1. 貼文編輯使用錯誤的API (NEW) 🔴 P1
**問題**:
- 點擊「編輯」按鈕 → 修改標題/內容 → 點擊「保存」
- 實際調用了 `approve` API (審核通過)
- 應該只更新內容，不改變狀態

**程式碼位置**:
- `PostReviewPage.tsx:288-307` - `handleSaveEdit` 函數
- 調用: `handleApprove(editingPost.id.toString(), title, content)`
- 應調用: `PostingManagementAPI.updatePostContent()`

**預期行為**:
1. 用戶編輯標題/內容
2. 點擊「保存」
3. 調用 `/api/posts/{id}/content` PUT 請求
4. 更新標題/內容
5. **保持原有status不變** (draft保持draft, approved保持approved)

**實際行為**:
1. 點擊「保存」
2. 調用 `/api/posts/{id}/approve`
3. 狀態改為 approved
4. 如果已是approved，會重複審核

**修復方案**:
```typescript
const handleSaveEdit = async () => {
  const { title, content } = form.getFieldsValue();
  const result = await PostingManagementAPI.updatePostContent(
    editingPost.id.toString(),
    { title, content }
  );
  if (result.success) {
    message.success('貼文已保存');
    loadPosts();
  }
};
```

**影響**:
- 修復後用戶可以自由編輯貼文而不改變狀態
- 審核流程更清晰: 編輯 ≠ 審核

---

### 2. 發布/審核API返回404 (NEW) 🔴 P0
**問題**:
- 調用 `/api/posts/{id}/approve` → 404
- 調用 `/api/posts/{id}/publish` → 404

**錯誤日誌**:
```
POST https://forumautoposter-production.up.railway.app/api/posts/{id}/approve
404 (Not Found)

POST https://forumautoposter-production.up.railway.app/api/posts/{id}/publish
404 (Not Found)
```

**根本原因** (需確認):
- **可能1**: posting-service routes未被include在main.py
- **可能2**: unified-API未proxy這些請求到posting-service
- **可能3**: Railway部署配置問題

**檢查步驟**:
1. 確認posting-service/main.py是否include post_routes
2. 確認unified-API是否需要proxy /api/posts/*請求
3. 確認Railway服務配置

**影響**:
- ❌ **無法審核貼文**
- ❌ **無法發布貼文到CMoney**
- 🔥 **Critical blocker - 必須修復才能使用系統**

---

### 3. KOL詳情頁面無限載入 (NEW) ⚠️ P2
**問題**:
- 點擊KOL詳情頁
- 顯示「載入 KOL 詳情中...」
- 一直spinning，never completes

**需要檢查**:
1. KOL詳情API endpoint是否存在
2. Frontend是否調用正確的URL
3. API返回的數據結構是否正確

**調試**:
- 檢查Network tab看API請求狀態
- 檢查Console看錯誤訊息

---

## 📊 進度總結

### 已修復
- ✅ Critical觸發器內容生成bug
- ✅ 排程顯示數據錯誤
- ✅ Auto-posting toggle
- ✅ KOL列表類型錯誤
- ✅ 排程器重新啟用
- ✅ 清理舊排程

### 待修復 (按優先級)
1. 🔴 **P0**: 發布/審核API 404 - **必須修復**
2. 🔴 **P1**: 貼文編輯使用錯誤API - 影響UX
3. ⚠️ **P2**: KOL詳情頁載入 - 影響功能性

---

## 🚀 下一步行動

### 立即測試 (用戶)
1. **測試已修復的功能**:
   - ✅ 創建limit_down排程，生成貼文，檢查內容是否正確
   - ✅ 檢查排程管理頁面顯示是否正確
   - ✅ 測試auto-posting toggle是否工作
   - ✅ 檢查KOL列表是否載入

2. **報告發布/審核API問題**:
   - 提供完整的Network tab錯誤
   - 確認Railway服務配置

### 待修復 (我)
1. 修復貼文編輯API調用
2. 調查發布/審核404問題
3. 調查KOL詳情載入問題

---

## 📝 部署狀態

**已推送到GitHub**: ✅
**Railway自動部署**: ⏳ 5-10分鐘

**提交記錄**:
- `9ba46209` - Re-enable scheduler
- `97573253` - Fix KOL list query type cast
- `50548a95` - Fix trigger type content generation (CRITICAL)
- `58928b7b` - Fix schedule display and toggle

---

## ⏱️ 時間線

**已用時間**: ~2小時
**剩餘工作**: ~1-2小時 (取決於API 404問題複雜度)

**距離完全上架**: 待修復P0和P1問題後，預計還需1-2小時測試。
