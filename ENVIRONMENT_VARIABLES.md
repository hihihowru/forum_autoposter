# 環境變數配置指南

## Vercel 環境變數設置

在 Vercel Dashboard 中設置以下環境變數：

### Production 環境
```
RAILWAY_API_URL=https://forumautoposter-production.up.railway.app
NODE_ENV=production
```

### Preview 環境
```
RAILWAY_API_URL=https://forumautoposter-production.up.railway.app
NODE_ENV=preview
```

### Development 環境
```
RAILWAY_API_URL=https://forumautoposter-production.up.railway.app
NODE_ENV=development
```

## Railway 環境變數設置

Railway 通常會自動設置以下環境變數：

### 自動設置的變數
```
PORT=8000 (Railway 自動分配)
NODE_ENV=production
```

### 可選的自定義變數
```
PYTHONPATH=/app
LOG_LEVEL=INFO
```

## 設置步驟

### Vercel 設置步驟：
1. 登入 Vercel Dashboard
2. 選擇你的專案
3. 進入 Settings > Environment Variables
4. 添加 `RAILWAY_API_URL` 變數
5. 選擇適用的環境 (Production, Preview, Development)
6. 重新部署

### Railway 設置步驟：
1. 登入 Railway Dashboard
2. 選擇你的服務
3. 進入 Variables 標籤
4. 添加必要的環境變數
5. 重新部署

## 驗證設置

部署完成後，可以通過以下方式驗證：

1. 檢查 Vercel Function Logs 中的 proxy 日誌
2. 檢查 Railway Logs 中的 API 請求
3. 測試前端 API 調用是否成功
