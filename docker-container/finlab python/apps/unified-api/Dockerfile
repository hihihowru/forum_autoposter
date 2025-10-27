# Workaround for Docker Hub 503 errors: Use specific version with digest
# This bypasses some of the Docker Hub auth issues by using cached layers
FROM python:3.11.9-slim-bookworm

# 設置工作目錄
WORKDIR /app

# 安裝系統依賴 (with retry logic for Railway network issues)
RUN apt-get update --fix-missing || apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 複製 requirements.txt 並安裝 Python 依賴 (with retry logic for Railway network issues)
COPY requirements.txt .
RUN pip install --no-cache-dir --retries 10 --timeout 300 -r requirements.txt || \
    pip install --no-cache-dir --retries 10 --timeout 300 -r requirements.txt || \
    pip install --no-cache-dir --retries 10 --timeout 300 -r requirements.txt

# 複製應用程式碼
COPY main.py .

# 複製 posting-service 模組 (GPT 和個人化模組需要)
# Note: posting-service directory should be in unified-api/ before Docker build
COPY posting-service/ ./posting-service/

# Note: stock_mapping.json and post_records are loaded from database or generated at runtime
# Removed COPY commands for files outside build context

# 暴露端口（Railway 會自動設置 PORT 環境變數）
EXPOSE $PORT

# 啟動應用
CMD ["python", "main.py"]
