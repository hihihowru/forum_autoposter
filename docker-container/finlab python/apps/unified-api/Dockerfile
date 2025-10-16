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

# 複製股票映射表
COPY ../../stock_mapping.json /app/stock_mapping.json

# 複製 post_records 數據
COPY ../../post_records_1788.json /app/post_records_1788.json

# 暴露端口（Railway 會自動設置 PORT 環境變數）
EXPOSE $PORT

# 啟動應用
CMD ["python", "main.py"]
