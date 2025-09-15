# Docker 架構優化建議

## 🏗️ **建議的新架構**

### **開發環境**
```
前端：本地開發 (npm run dev) - port 3000
├── 後端服務：Docker 管理
│   ├── dashboard-api (port 8007)
│   ├── dashboard-backend (port 8012) 
│   ├── trending-api (port 8004)
│   ├── posting-service (port 8001)
│   ├── ohlc-api (port 8005)
│   ├── analyze-api (port 8002)
│   ├── summary-api (port 8003)
│   ├── financial-api (port 8006)
│   └── postgres-db (port 5432)
```

### **生產環境**
```
所有服務都用 Docker
├── 前端：Docker (構建後的靜態文件)
├── 後端：Docker
└── 資料庫：Docker
```

## 📋 **具體優化步驟**

### 1. **創建開發用 Docker Compose**
- 移除前端服務
- 保留所有後端服務
- 優化端口配置

### 2. **創建生產用 Docker Compose**
- 包含前端服務（構建後的靜態文件）
- 包含所有後端服務
- 優化部署配置

### 3. **前端開發流程**
- 本地運行 `npm run dev`
- 通過代理訪問後端服務
- 熱重載開發體驗

## 🚀 **優化後的好處**

1. **開發效率**：前端熱重載，後端穩定運行
2. **資源節省**：不需要重複構建前端
3. **架構清晰**：開發和生產環境分離
4. **維護簡單**：減少重複配置
