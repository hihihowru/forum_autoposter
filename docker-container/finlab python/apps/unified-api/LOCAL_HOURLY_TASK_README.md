# 🕐 本地每小時任務設置指南

由於 Railway 不支持 OpenVPN，我們改用本地 Mac 運行每小時任務。

## 📋 工作原理

1. **本地 Mac** (有 VPN 權限):
   - 每小時從 CMoney 抓取新文章 (透過 VPN)
   - 使用 KOL 帳號按讚
   - 儲存統計到 Railway PostgreSQL

2. **Railway Backend**:
   - 提供 API 給前端
   - 儲存數據庫
   - 前端從數據庫讀取統計數據

## 🚀 快速開始

### 選項 A: 自動設置 (推薦)

```bash
cd "/Users/willchen/Documents/autoposter/forum_autoposter/docker-container/finlab python/apps/unified-api"
./setup_local_cron.sh
```

這個腳本會:
1. 要求你輸入 Railway DATABASE_URL
2. 測試腳本是否能運行
3. 自動設置 cronjob

### 選項 B: 手動設置

#### 1. 設置環境變數

```bash
# 獲取 Railway 數據庫 URL
railway variables --service forum_autoposter | grep DATABASE_URL

# 創建環境變數文件
cat > ~/.hourly_task_env <<EOF
export DATABASE_URL="postgresql://postgres:PASSWORD@HOST:PORT/railway"
EOF

chmod 600 ~/.hourly_task_env
```

#### 2. 測試腳本

```bash
cd "/Users/willchen/Documents/autoposter/forum_autoposter/docker-container/finlab python/apps/unified-api"
source ~/.hourly_task_env
python3 local_hourly_task.py
```

你應該看到類似:
```
🚀 開始執行本地每小時任務...
📥 開始抓取過去 1 小時的文章...
✅ 找到 2462 篇新文章
❤️  開始執行按讚任務...
📊 執行結果:
   總文章數: 2462
   成功按讚: 2450
   成功率: 99.51%
✅ 本地每小時任務執行完成!
```

#### 3. 設置 Cronjob

```bash
crontab -e
```

添加以下行 (每小時的第 0 分鐘執行):
```cron
0 * * * * source ~/.hourly_task_env && cd "/Users/willchen/Documents/autoposter/forum_autoposter/docker-container/finlab python/apps/unified-api" && /usr/bin/python3 local_hourly_task.py >> /tmp/hourly_task.log 2>&1
```

## 📊 監控

### 查看日誌

```bash
# 實時查看日誌
tail -f /tmp/hourly_task.log

# 查看最後 50 行
tail -50 /tmp/hourly_task.log
```

### 查看 Cronjob

```bash
# 列出所有 cronjob
crontab -l

# 編輯 cronjob
crontab -e

# 刪除所有 cronjob (小心!)
crontab -r
```

### 檢查數據庫

前往 Railway 網頁查看:
```bash
curl "https://forumautoposter-production.up.railway.app/api/reaction-bot/hourly-stats/latest"
```

或查看最近 24 小時:
```bash
curl "https://forumautoposter-production.up.railway.app/api/reaction-bot/hourly-stats?limit=24"
```

## 🔧 故障排除

### Cronjob 沒有運行

1. 檢查 cron 是否啟動:
   ```bash
   sudo launchctl list | grep cron
   ```

2. 檢查環境變數文件權限:
   ```bash
   ls -la ~/.hourly_task_env
   # 應該是 -rw------- (600)
   ```

3. 測試手動運行:
   ```bash
   source ~/.hourly_task_env && python3 local_hourly_task.py
   ```

### 數據庫連接失敗

1. 確認 DATABASE_URL 正確:
   ```bash
   echo $DATABASE_URL
   ```

2. 測試數據庫連接:
   ```bash
   railway run python3 check_db_tables.py
   ```

### CMoney API 超時

確保你的 Mac 連接到 CMoney VPN:
```bash
# 檢查 VPN 連接
ifconfig | grep tun
```

## 📅 Cronjob 時間表說明

```cron
# 分 時 日 月 週
# 0 * * * *  - 每小時的第 0 分鐘
# */30 * * * *  - 每 30 分鐘
# 0 */2 * * *  - 每 2 小時
# 0 9 * * *  - 每天早上 9 點
# 0 9 * * 1-5  - 週一到週五早上 9 點
```

## 🎯 下一步

一旦設置完成:
1. ✅ 每小時自動抓取文章並按讚
2. ✅ 數據自動儲存到 Railway 數據庫
3. ✅ 前端可以從 Railway 讀取統計數據顯示

**前端 URL**: https://forumautoposter-production.up.railway.app/engagement-management

---

**最後更新**: 2025-11-13
