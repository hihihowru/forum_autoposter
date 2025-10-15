# 互動數據刷新功能

## 🎯 功能概述

在互動總覽頁面新增了**刷新按鈕**，可以自動更新所有歷史Article ID的互動數據到Google Sheets，然後從Google Sheets重新獲取最新數據。

## ✅ 功能特點

### 1. 自動化刷新
- 一鍵刷新所有歷史Article ID的互動數據
- 自動從Google Sheets的貼文記錄表獲取Article ID列表
- 批量調用CMoney API獲取最新互動數據

### 2. 數據更新
- 自動更新Google Sheets中的互動回饋表格
- 支持多個時間週期：1小時、1日、7日
- 包含完整的互動數據：讚數、留言數、分享數、瀏覽數、互動率

### 3. 用戶體驗
- 前端顯示刷新進度
- 後台異步處理，不阻塞用戶操作
- 實時狀態反饋和錯誤處理

## 🚀 使用方法

### 1. 前端操作
1. 進入**互動分析** > **互動總覽**頁面
2. 點擊右上角的**"刷新數據"**按鈕
3. 系統會顯示"刷新任務已啟動，數據將在後台更新"
4. 等待幾分鐘後，數據會自動更新

### 2. API端點
```http
POST /api/interaction/refresh
Content-Type: application/json

{
  "force_refresh": true,
  "article_ids": null  // 可選：指定要刷新的Article ID列表
}
```

### 3. 響應格式
```json
{
  "success": true,
  "message": "刷新任務已啟動，請稍後查看結果",
  "task_id": "refresh_20240827_112543",
  "start_time": "2024-08-27T11:25:43"
}
```

## 🔧 技術實現

### 1. 後端API
- **文件**: `docker-container/finlab python/apps/dashboard-api/interaction_refresh.py`
- **功能**: 提供互動數據刷新服務
- **特點**: 支持背景任務處理，避免API超時

### 2. 前端組件
- **文件**: `docker-container/finlab python/apps/dashboard-frontend/src/components/Dashboard/InteractionAnalysis.tsx`
- **功能**: 添加刷新按鈕和狀態管理
- **特點**: 實時狀態反饋，用戶友好的界面

### 3. 數據流程
```
1. 用戶點擊刷新按鈕
2. 前端發送POST請求到 /api/interaction/refresh
3. 後端啟動背景任務
4. 從Google Sheets獲取所有Article ID
5. 批量調用CMoney API獲取互動數據
6. 更新Google Sheets中的互動回饋表格
7. 前端自動刷新顯示最新數據
```

## 📊 數據結構

### 互動回饋表格欄位
| 欄位 | 說明 | 數據類型 |
|------|------|----------|
| Article ID | 文章ID | 文字 |
| Member ID | 會員ID | 文字 |
| 暱稱 | KOL暱稱 | 文字 |
| 標題 | 文章標題 | 文字 |
| 生成內文 | 文章內容 | 文字 |
| Topic ID | 話題ID | 文字 |
| 是否為熱門話題 | 熱門話題標記 | 布林值 |
| 發文時間 | 發文時間 | 日期時間 |
| 最後更新時間 | 最後更新時間 | 日期時間 |
| 讚數 | 按讚數量 | 數字 |
| 留言數 | 留言數量 | 數字 |
| 總互動數 | 總互動數量 | 數字 |
| 互動率 | 互動率 | 浮點數 |
| 成長率 | 成長率 | 浮點數 |
| 收集錯誤 | 錯誤訊息 | 文字 |

## ⚙️ 配置說明

### 1. 環境變數
```bash
GOOGLE_CREDENTIALS_FILE=./credentials/google-service-account.json
GOOGLE_SHEETS_ID=148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LikN2s
```

### 2. KOL憑證
目前使用川川哥的憑證進行API調用：
- Email: `forum_200@cmoney.com.tw`
- Password: `N9t1kY3x`

### 3. API限制
- 每次請求間隔0.5秒，避免API限制
- 每處理10個Article就更新一次Google Sheets
- 支持批量處理，提高效率

## 🎯 使用場景

### 1. 定期數據更新
- 每日或每週定期刷新互動數據
- 確保儀表板顯示最新的互動統計

### 2. 數據分析
- 獲取最新的互動趨勢
- 分析KOL表現和內容效果

### 3. 報告生成
- 為管理層提供最新的互動報告
- 支持決策制定和策略調整

## ⚠️ 注意事項

### 1. API限制
- CMoney API有頻率限制，大量刷新可能需要較長時間
- 建議在非高峰時段進行批量刷新

### 2. 數據準確性
- 刷新過程中可能會有短暫的數據不一致
- 建議等待刷新完成後再進行數據分析

### 3. 錯誤處理
- 如果某個Article ID無法獲取數據，會記錄錯誤但繼續處理其他ID
- 可以通過錯誤日誌查看具體的失敗原因

## 🔍 故障排除

### 1. 刷新失敗
- 檢查CMoney API憑證是否有效
- 確認Google Sheets權限設置
- 查看後端日誌了解具體錯誤

### 2. 數據不更新
- 確認刷新任務是否成功啟動
- 檢查Google Sheets中的數據是否已更新
- 嘗試手動刷新前端頁面

### 3. 性能問題
- 如果Article ID數量很多，刷新可能需要較長時間
- 可以考慮分批刷新或優化API調用頻率

## 📈 未來改進

### 1. 功能增強
- 支持指定時間範圍的刷新
- 添加刷新進度條和詳細狀態
- 支持增量刷新（只更新有變化的數據）

### 2. 性能優化
- 實現並發API調用
- 添加數據緩存機制
- 優化Google Sheets更新策略

### 3. 用戶體驗
- 添加刷新歷史記錄
- 支持定時自動刷新
- 提供刷新結果通知

---

**總結**: 互動數據刷新功能已經成功實現，可以一鍵更新所有歷史Article ID的互動數據，為儀表板提供最新、最準確的互動統計信息！



