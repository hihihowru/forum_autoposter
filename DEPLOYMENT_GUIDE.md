# 發文管理系統部署指南

## 🚀 快速開始

### 本地開發環境

1. **啟動數據庫服務**
```bash
# 使用Docker Compose啟動PostgreSQL和Redis
docker-compose -f docker-compose.posting.yml up -d postgres redis

# 或者手動安裝PostgreSQL
# macOS: brew install postgresql
# Ubuntu: sudo apt-get install postgresql
```

2. **初始化數據庫**
```bash
# 運行數據庫初始化腳本
python init_database.py

# 或者手動創建數據庫
createdb posting_management
```

3. **啟動後端服務**
```bash
cd docker-container/finlab\ python/apps/dashboard-backend
pip install -r requirements.txt
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

4. **啟動前端服務**
```bash
cd docker-container/finlab\ python/apps/dashboard-frontend
npm install
npm run dev
```

5. **訪問應用**
- 前端: http://localhost:3000
- 後端API: http://localhost:8000
- API文檔: http://localhost:8000/docs

## ☁️ 雲端部署

### AWS 部署

1. **創建RDS PostgreSQL實例**
```bash
aws rds create-db-instance \
  --db-instance-identifier posting-management-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username postgres \
  --master-user-password your-password \
  --allocated-storage 20
```

2. **創建ElastiCache Redis實例**
```bash
aws elasticache create-cache-cluster \
  --cache-cluster-id posting-management-redis \
  --cache-node-type cache.t3.micro \
  --engine redis \
  --num-cache-nodes 1
```

3. **部署到ECS**
```bash
# 構建Docker鏡像
docker build -t posting-management-backend ./docker-container/finlab\ python/apps/dashboard-backend
docker build -t posting-management-frontend ./docker-container/finlab\ python/apps/dashboard-frontend

# 推送到ECR
aws ecr create-repository --repository-name posting-management-backend
aws ecr create-repository --repository-name posting-management-frontend

# 部署到ECS
aws ecs create-service \
  --cluster your-cluster \
  --service-name posting-management \
  --task-definition posting-management-task \
  --desired-count 2
```

### GCP 部署

1. **創建Cloud SQL實例**
```bash
gcloud sql instances create posting-management-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=asia-east1
```

2. **創建Memorystore Redis實例**
```bash
gcloud redis instances create posting-management-redis \
  --size=1 \
  --region=asia-east1
```

3. **部署到Cloud Run**
```bash
# 構建並部署後端
gcloud run deploy posting-management-backend \
  --source ./docker-container/finlab\ python/apps/dashboard-backend \
  --platform managed \
  --region asia-east1

# 構建並部署前端
gcloud run deploy posting-management-frontend \
  --source ./docker-container/finlab\ python/apps/dashboard-frontend \
  --platform managed \
  --region asia-east1
```

### Azure 部署

1. **創建PostgreSQL數據庫**
```bash
az postgres server create \
  --resource-group myResourceGroup \
  --name posting-management-db \
  --location eastasia \
  --admin-user postgres \
  --admin-password your-password \
  --sku-name B_Gen5_1
```

2. **創建Redis緩存**
```bash
az redis create \
  --resource-group myResourceGroup \
  --name posting-management-redis \
  --location eastasia \
  --sku Basic \
  --vm-size c0
```

3. **部署到App Service**
```bash
# 創建App Service計劃
az appservice plan create \
  --name posting-management-plan \
  --resource-group myResourceGroup \
  --sku B1

# 部署後端
az webapp create \
  --resource-group myResourceGroup \
  --plan posting-management-plan \
  --name posting-management-backend

# 部署前端
az webapp create \
  --resource-group myResourceGroup \
  --plan posting-management-plan \
  --name posting-management-frontend
```

## 🔧 環境變數配置

### 開發環境
```bash
# .env.development
DATABASE_URL=postgresql://postgres:password@localhost:5432/posting_management
REDIS_URL=redis://localhost:6379
API_BASE_URL=http://localhost:8000
ENVIRONMENT=development
```

### 生產環境
```bash
# .env.production
DATABASE_URL=postgresql://user:pass@prod-db:5432/posting_management
REDIS_URL=redis://prod-redis:6379
API_BASE_URL=https://api.posting-management.com
ENVIRONMENT=production
SECRET_KEY=your-secret-key
```

## 📊 數據備份

### 自動備份腳本
```bash
#!/bin/bash
# backup.sh

# 數據庫備份
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).sql

# 上傳到雲端存儲
aws s3 cp backup_$(date +%Y%m%d_%H%M%S).sql s3://backup-bucket/database/

# 清理本地備份文件
rm backup_*.sql
```

### 定時備份
```bash
# 添加到crontab
0 2 * * * /path/to/backup.sh
```

## 🔍 監控和日誌

### 應用監控
- **後端**: 使用FastAPI的內建監控
- **前端**: 使用Sentry進行錯誤追蹤
- **數據庫**: 使用pgAdmin或DataGrip

### 日誌管理
```bash
# 後端日誌
docker logs posting_management_backend

# 數據庫日誌
docker logs posting_management_db

# 前端日誌
docker logs posting_management_frontend
```

## 🚨 故障排除

### 常見問題

1. **數據庫連接失敗**
```bash
# 檢查數據庫狀態
docker ps | grep postgres

# 檢查連接
psql -h localhost -U postgres -d posting_management
```

2. **API調用失敗**
```bash
# 檢查後端服務
curl http://localhost:8000/health

# 檢查API文檔
open http://localhost:8000/docs
```

3. **前端無法加載**
```bash
# 檢查前端服務
curl http://localhost:3000

# 檢查控制台錯誤
# 打開瀏覽器開發者工具
```

### 性能優化

1. **數據庫優化**
```sql
-- 創建索引
CREATE INDEX idx_posts_status ON posts(status);
CREATE INDEX idx_posts_created_at ON posts(created_at);
CREATE INDEX idx_posts_kol_serial ON posts(kol_serial);
```

2. **緩存優化**
```python
# Redis緩存配置
CACHE_TTL = 3600  # 1小時
CACHE_PREFIX = "posting_management:"
```

3. **前端優化**
```javascript
// 啟用代碼分割
const PostingGenerator = lazy(() => import('./PostingGenerator'));
const PostingReview = lazy(() => import('./PostingReview'));
```

## 📈 擴展性考慮

### 水平擴展
- 使用負載均衡器
- 數據庫讀寫分離
- Redis集群

### 垂直擴展
- 增加服務器資源
- 優化數據庫配置
- 使用CDN加速

## 🔒 安全考慮

### 數據安全
- 使用HTTPS
- 數據庫加密
- 定期安全更新

### 訪問控制
- API認證
- 角色權限管理
- 審計日誌

## 📞 支援

如有問題，請聯繫：
- 技術支援: tech-support@posting-management.com
- 文檔: https://docs.posting-management.com
- GitHub: https://github.com/your-org/posting-management
