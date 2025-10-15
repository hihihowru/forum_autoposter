# 使用Python 3.11官方鏡像
FROM python:3.11-slim

# 設置工作目錄
WORKDIR /app

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 複製requirements文件
COPY requirements.txt .

# 安裝Python依賴
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用代碼
COPY . .

# 創建credentials目錄
RUN mkdir -p credentials

# 設置環境變數
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1

# 創建非root用戶
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# 健康檢查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# 默認命令
CMD ["python", "batch_post_publisher.py"]










