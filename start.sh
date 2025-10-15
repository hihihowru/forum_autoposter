#!/bin/bash

# Railway 部署啟動腳本
echo "🚀 啟動 Forum Autoposter API Gateway..."

# 設置環境變數
export PYTHONPATH="/app:$PYTHONPATH"
export PORT=${PORT:-8000}

echo "📋 環境變數:"
echo "  PORT: $PORT"
echo "  PYTHONPATH: $PYTHONPATH"

# 進入 API 網關目錄
cd docker-container/finlab\ python/apps/api-gateway

# 檢查文件是否存在
if [ ! -f "main.py" ]; then
    echo "❌ 找不到 main.py 文件"
    ls -la
    exit 1
fi

# 安裝依賴
echo "📦 安裝依賴..."
pip install -r requirements.txt

# 啟動服務
echo "🌟 啟動 API 網關服務在端口 $PORT..."
uvicorn main:app --host 0.0.0.0 --port $PORT