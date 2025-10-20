FROM python:3.11-slim

# 設置工作目錄
WORKDIR /app

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 複製 requirements.txt 並安裝 Python 依賴
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

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
