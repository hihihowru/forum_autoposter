# n8n-migration 專案啟動指南

## 🚀 快速啟動

### macOS/Linux 用戶
```bash
# 啟動所有服務 (後端 + 前端)
./start.sh

# 只啟動後端 Docker 服務
./start.sh backend

# 只啟動前端本地服務
./start.sh frontend

# 停止所有服務
./start.sh stop

# 查看服務狀態
./start.sh status

# 查看幫助
./start.sh help
```

### Windows 用戶
```cmd
REM 啟動所有服務 (後端 + 前端)
start.bat

REM 只啟動後端 Docker 服務
start.bat backend

REM 只啟動前端本地服務
start.bat frontend

REM 停止所有服務
start.bat stop

REM 查看服務狀態
start.bat status

REM 查看幫助
start.bat help
```

## 📋 系統要求

### 必需軟體
- **Docker** - 運行後端服務
- **Docker Compose** - 管理多容器應用
- **Node.js** (v16+) - 前端開發環境
- **npm** - Node.js 套件管理器

### 檢查安裝
腳本會自動檢查所有依賴是否已安裝。

## 🔧 服務架構

### 後端服務 (Docker)
| 服務名稱 | 端口 | 功能 |
|---------|------|------|
| PostgreSQL | 5432 | 數據庫 |
| Posting API | 8001 | 發文服務 |
| Revenue API | 8008 | 營收數據 |
| Dashboard API | 8007 | 儀表板 API |
| Dashboard Backend | 8012 | 儀表板後端 |
| Trending API | 8004 | 熱門話題 |
| Summary API | 8003 | 摘要服務 |
| Analyze API | 8002 | 分析服務 |
| OHLC API | 8005 | 股價數據 |
| Financial API | 8006 | 財務數據 |
| Monthly Revenue | 8009 | 月度營收 |
| Fundamental Analyzer | 8010 | 基本面分析 |

### 前端服務 (本地)
| 服務名稱 | 端口 | 功能 |
|---------|------|------|
| Dashboard Frontend | 3000 | 儀表板前端 |

## 🎯 使用流程

1. **首次啟動**
   ```bash
   ./start.sh
   ```
   - 自動檢查依賴
   - 停止現有服務
   - 構建並啟動後端服務
   - 安裝前端依賴
   - 啟動前端開發服務器

2. **日常開發**
   ```bash
   # 如果只需要重啟後端
   ./start.sh backend
   
   # 如果只需要重啟前端
   ./start.sh frontend
   ```

3. **停止服務**
   ```bash
   ./start.sh stop
   ```

## 🔍 故障排除

### 常見問題

1. **端口被佔用**
   ```bash
   # 查看端口使用情況
   lsof -i :3000  # macOS/Linux
   netstat -ano | findstr :3000  # Windows
   
   # 停止佔用端口的進程
   ./start.sh stop
   ```

2. **Docker 服務啟動失敗**
   ```bash
   # 查看 Docker 日誌
   docker-compose -f docker-compose.full.yml logs
   
   # 重新構建服務
   docker-compose -f docker-compose.full.yml up -d --build
   ```

3. **前端依賴安裝失敗**
   ```bash
   # 清理並重新安裝
   cd "docker-container/finlab python/apps/dashboard-frontend"
   rm -rf node_modules package-lock.json
   npm install
   ```

### 手動操作

如果腳本無法正常工作，可以手動執行：

```bash
# 1. 啟動後端服務
docker-compose -f docker-compose.full.yml up -d

# 2. 安裝前端依賴
cd "docker-container/finlab python/apps/dashboard-frontend"
npm install

# 3. 啟動前端服務
npm run dev
```

## 📝 注意事項

- 前端服務運行在本地，不在 Docker 中
- 確保端口 3000 和 8001-8012 沒有被其他服務佔用
- 首次啟動可能需要較長時間來下載和構建 Docker 鏡像
- 前端服務支援熱重載，修改代碼會自動刷新

## 🆘 獲取幫助

如果遇到問題，請：
1. 檢查系統依賴是否正確安裝
2. 查看服務日誌：`docker-compose -f docker-compose.full.yml logs`
3. 確認端口沒有被佔用
4. 嘗試重新構建服務：`docker-compose -f docker-compose.full.yml up -d --build`

