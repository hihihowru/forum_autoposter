# CRITICAL: Docker Hub auth is completely down (502/503 errors)
# Using full python:3.11 image which Railway likely has cached
# Full image is larger but should work without hitting Docker Hub auth
FROM python:3.11

# 設置工作目錄
WORKDIR /app

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 複製所有應用代碼（包括 unified-api 和啟動腳本）
COPY . .

# 複製股票映射表到正確位置（COPY . . 已經複製了，這裡只是確保位置正確）
RUN cp "docker-container/finlab python/stock_mapping.json" /app/stock_mapping.json || echo "stock_mapping.json not found, will use fallback"

# 複製並安裝 unified-api 的依賴（使用 JSON array 語法處理空格路徑）
# CACHE BUST 2025-10-20 17:54 - Force rebuild to install sqlalchemy
COPY ["docker-container/finlab python/apps/unified-api/requirements.txt", "/tmp/requirements.txt"]
RUN pip install --no-cache-dir --force-reinstall -r /tmp/requirements.txt

# 創建credentials目錄
RUN mkdir -p credentials

# 設置環境變數
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# 創建非root用戶
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# 健康檢查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# 暴露端口
EXPOSE $PORT

# 使用啟動腳本（它會 cd 到正確的目錄並啟動服務）
CMD ["sh", "start-unified-api.sh"]