#!/bin/bash

# Railway 部署啟動腳本
echo "🚀 啟動 Forum Autoposter API Gateway..."

# 設置環境變數
export PYTHONPATH="/app:$PYTHONPATH"
export PORT=${PORT:-8000}

# 進入 API 網關目錄
cd docker-container/finlab\ python/apps/api-gateway

# 安裝依賴
echo "📦 安裝依賴..."
pip install -r requirements.txt

# 啟動服務
echo "🌟 啟動 API 網關服務..."
uvicorn main:app --host 0.0.0.0 --port $PORT