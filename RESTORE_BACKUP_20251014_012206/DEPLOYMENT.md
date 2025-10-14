# 批次發文系統部署腳本

## 本地運行
```bash
# 直接運行批次發文
python3 batch_post_publisher.py
```

## Docker 部署

### 1. 構建並運行容器
```bash
# 構建Docker鏡像
docker build -t batch-post-publisher .

# 運行容器
docker run -d \
  --name batch-post-publisher \
  -v $(pwd)/credentials:/app/credentials:ro \
  -v $(pwd)/.env:/app/.env:ro \
  -v $(pwd)/logs:/app/logs \
  batch-post-publisher
```

### 2. 使用 Docker Compose
```bash
# 啟動服務
docker-compose up -d

# 查看日誌
docker-compose logs -f batch-post-publisher

# 停止服務
docker-compose down
```

### 3. 生產環境部署
```bash
# 使用docker-compose.yml
docker-compose -f docker-compose.yml up -d

# 查看容器狀態
docker ps

# 查看日誌
docker logs -f batch-post-publisher
```

## 監控和維護

### 查看日誌
```bash
# 實時日誌
docker logs -f batch-post-publisher

# 最近100行日誌
docker logs --tail 100 batch-post-publisher
```

### 重啟服務
```bash
# 重啟容器
docker restart batch-post-publisher

# 或使用docker-compose
docker-compose restart batch-post-publisher
```

### 更新代碼
```bash
# 重新構建並部署
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## 環境變數配置

確保 `.env` 文件包含必要的環境變數：
```env
SERPER_API_KEY=your_serper_api_key
OPENAI_API_KEY=your_openai_api_key
```

## 憑證文件

確保 `credentials/google-service-account.json` 文件存在且有效。

## 故障排除

### 常見問題
1. **憑證錯誤**: 檢查Google服務帳號憑證文件
2. **網絡問題**: 確保容器能訪問外部API
3. **權限問題**: 檢查文件掛載權限

### 調試模式
```bash
# 以調試模式運行
docker run -it --rm \
  -v $(pwd)/credentials:/app/credentials:ro \
  -v $(pwd)/.env:/app/.env:ro \
  batch-post-publisher \
  python -u batch_post_publisher.py
```










