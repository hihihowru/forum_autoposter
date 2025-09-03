# Google Sheets API 設置指南

## 步驟 1: 創建 Google Cloud 專案

1. 前往 [Google Cloud Console](https://console.cloud.google.com/)
2. 點擊 "Select a project" > "New Project"
3. 輸入專案名稱: `n8n-migration-project`
4. 點擊 "Create"

## 步驟 2: 啟用必要的 API

1. 在左側選單中選擇 "APIs & Services" > "Library"
2. 搜尋並啟用以下 API：
   - **Google Sheets API**
   - **Google Drive API** (可選，用於文件管理)

## 步驟 3: 創建 Service Account

**重要：選擇 Service Account，不是 OAuth 2.0**

1. 前往 "APIs & Services" > "Credentials"
2. 點擊 "Create Credentials" > "Service Account" （**不要選擇 OAuth 2.0 用戶端 ID**）
3. 填寫 Service Account 詳情：
   - **Service account name**: `n8n-migration-service`
   - **Service account ID**: `n8n-migration-service` (自動生成)
   - **Description**: `Service account for N8N migration project`
4. 點擊 "Create and Continue"
5. 跳過角色分配 (點擊 "Continue")
6. 跳過授予用戶存取權 (點擊 "Done")

**注意：不要創建 OAuth 2.0 用戶端 ID，那是給需要用戶授權的應用程式使用的。**

## 步驟 4: 下載憑證檔案

1. 在 Credentials 頁面找到剛創建的 Service Account
2. 點擊 Service Account 名稱
3. 前往 "Keys" 標籤
4. 點擊 "Add Key" > "Create new key"
5. 選擇 "JSON" 格式
6. 下載 JSON 檔案

## 步驟 5: 設置 Google Sheets 權限

1. 打開你的 Google Sheets 文件: [aigc 自我學習機制](https://docs.google.com/spreadsheets/d/148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LikN2s/edit)
2. 點擊右上角的 "Share" 按鈕
3. 在 "Add people and groups" 中輸入 Service Account 的 email
   - 格式: `n8n-migration-service@your-project-id.iam.gserviceaccount.com`
4. 設置權限為 "Editor"
5. 點擊 "Send"

## 步驟 6: 配置憑證檔案

1. 將下載的 JSON 檔案放到專案的 `credentials/` 目錄
2. 重命名為 `google-service-account.json`
3. 確保檔案結構如下：
   ```
   credentials/
   └── google-service-account.json
   ```

## 步驟 7: 測試連接

運行測試腳本：
```bash
python test_google_sheets.py
```

如果測試成功，你會看到：
```
✅ Google Sheets API 連接測試成功！
可以開始使用 Google Sheets 整合功能
```

## 故障排除

### 常見錯誤

1. **憑證檔案不存在**
   - 確保 JSON 檔案在 `credentials/` 目錄中
   - 檢查檔案名稱是否為 `google-service-account.json`

2. **權限不足**
   - 確保 Service Account 有 Google Sheets 編輯權限
   - 檢查 Service Account email 是否正確添加到 Google Sheets

3. **API 未啟用**
   - 確保 Google Sheets API 已啟用
   - 檢查 Google Cloud 專案是否正確

4. **文件 ID 錯誤**
   - 確保 Google Sheets 文件 ID 正確
   - 文件 ID: `148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LikN2s`

### 檢查清單

- [ ] Google Cloud 專案已創建
- [ ] Google Sheets API 已啟用
- [ ] Service Account 已創建
- [ ] JSON 憑證檔案已下載
- [ ] 憑證檔案已放到 `credentials/` 目錄
- [ ] Service Account 已添加到 Google Sheets 編輯權限
- [ ] 測試腳本運行成功

## 下一步

設置完成後，你可以：
1. 開始實作 CMoney API 客戶端
2. 建立話題派發服務
3. 實作內容生成服務
4. 設置發文服務
