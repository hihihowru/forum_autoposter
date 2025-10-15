# 服務啟動指南

## 快速啟動（推薦）

### 方法1：使用啟動腳本
```bash
# 啟動所有服務
./start_services.sh

# 停止所有服務
./stop_services.sh
```

### 方法2：使用 Docker Compose
```bash
# 啟動所有服務
docker-compose up -d

# 停止所有服務
docker-compose down

# 查看服務狀態
docker-compose ps
```

## 服務列表

| 服務名稱 | 端口 | 描述 |
|---------|------|------|
| posting-service | 8001 | 貼文生成服務 |
| ohlc-api | 8005 | 股票數據API |
| analyze-api | 8002 | 技術分析API |
| summary-api | 8003 | 內容摘要API |
| trending-api | 8004 | 熱門話題API |
| dashboard-api | 8007 | 儀表板API |
| financial-api | 8006 | 財務數據API |

## 檢查服務狀態

```bash
# 檢查特定端口
lsof -i :8001

# 檢查所有服務端口
lsof -i :8001,8002,8003,8004,8005,8006,8007
```

## 故障排除

1. **端口被占用**：使用 `lsof -i :端口號` 查看占用進程
2. **服務啟動失敗**：檢查日誌 `docker-compose logs 服務名`
3. **服務間通信問題**：確保所有服務都在同一網絡中



















