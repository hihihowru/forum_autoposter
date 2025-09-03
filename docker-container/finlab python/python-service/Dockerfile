# 使用官方 Python 映像檔
FROM python:3.10-slim

# 設定工作目錄
WORKDIR /app

# 複製 requirements 並安裝
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製整個專案（包括 get_ohlc.py）
COPY . .

# 暴露 port
EXPOSE 8000

# 啟動 FastAPI 應用
CMD ["uvicorn", "get_ohlc:app", "--host", "0.0.0.0", "--port", "8000"]