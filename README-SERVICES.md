# FinLab API 服務快速啟動指南

## 🚀 快速開始

### 1. 啟動核心服務（推薦）
```bash
./manage-services.sh start core
```

### 2. 啟動所有服務
```bash
./manage-services.sh start all
```

### 3. 檢查服務狀態
```bash
./manage-services.sh status
```

### 4. 檢查服務健康狀態
```bash
./manage-services.sh health
```

## 📋 服務清單

### 🟢 核心服務 (Core Services)
| 服務名稱 | 端口 | 功能描述 | 依賴 |
|---------|------|----------|------|
| **posting-service** | 8001 | 主要發文服務 | trending-api, ohlc-api, analyze-api, financial-api, summary-api |
| **ohlc-api** | 8005 | 股價數據API (FinLab) | - |
| **analyze-api** | 8002 | 技術分析API | - |
| **summary-api** | 8003 | 摘要分析API | ohlc-api, analyze-api |
| **trending-api** | 8004 | 熱門話題API | - |
| **financial-api** | 8006 | 財務數據API | - |
| **dashboard-api** | 8007 | 儀表板API | - |

### 🔵 數據服務 (Data Services)
| 服務名稱 | 端口 | 功能描述 |
|---------|------|----------|
| **revenue-api** | 8008 | 營收數據API |
| **monthly-revenue-api** | 8009 | 月營收API |

### 🟡 分析服務 (Analysis Services)
| 服務名稱 | 端口 | 功能描述 |
|---------|------|----------|
| **fundamental-analyzer** | 8010 | 基本面分析API |

### 🟣 內容服務 (Content Services)
| 服務名稱 | 端口 | 功能描述 | 依賴 |
|---------|------|----------|------|
| **auto-publisher** | 8011 | 自動發布服務 | posting-service |

### 🟠 儀表板服務 (Dashboard Services)
| 服務名稱 | 端口 | 功能描述 | 依賴 |
|---------|------|----------|------|
| **dashboard-backend** | 8012 | 儀表板後端 | - |
| **dashboard-frontend** | 3000 | 儀表板前端 | dashboard-api |

### 🔴 訓練服務 (Training Services)
| 服務名稱 | 端口 | 功能描述 |
|---------|------|----------|
| **trainer** | 8013 | 訓練服務 |

## 🛠️ 管理命令

### 啟動服務
```bash
# 啟動核心服務
./manage-services.sh start core

# 啟動數據服務
./manage-services.sh start data

# 啟動分析服務
./manage-services.sh start analysis

# 啟動內容服務
./manage-services.sh start content

# 啟動儀表板服務
./manage-services.sh start dashboard

# 啟動訓練服務
./manage-services.sh start training

# 啟動所有服務
./manage-services.sh start all

# 啟動特定服務
./manage-services.sh start posting-service
```

### 停止服務
```bash
# 停止核心服務
./manage-services.sh stop core

# 停止所有服務
./manage-services.sh stop all

# 停止特定服務
./manage-services.sh stop posting-service
```

### 重啟服務
```bash
# 重啟核心服務
./manage-services.sh restart core

# 重啟所有服務
./manage-services.sh restart all

# 重啟特定服務
./manage-services.sh restart posting-service
```

### 監控服務
```bash
# 查看服務狀態
./manage-services.sh status

# 查看服務日誌
./manage-services.sh logs posting-service

# 檢查服務健康狀態
./manage-services.sh health
```

### 維護操作
```bash
# 清理停止的容器
./manage-services.sh clean

# 重新構建服務
./manage-services.sh rebuild posting-service
```

## 🔧 配置文件

- `docker-compose.full.yml` - 完整的 Docker Compose 配置
- `docker-compose.yml` - 核心服務的 Docker Compose 配置
- `services.conf` - 服務配置文件
- `manage-services.sh` - 服務管理腳本

## 📝 使用建議

1. **開發環境**: 建議只啟動核心服務 `./manage-services.sh start core`
2. **測試環境**: 可以啟動所有服務 `./manage-services.sh start all`
3. **生產環境**: 根據需要選擇性啟動服務

## 🚨 注意事項

1. 確保 `.env` 文件已正確配置
2. 某些服務需要 FinLab API 認證
3. 服務間有依賴關係，請按順序啟動
4. 定期檢查服務健康狀態
