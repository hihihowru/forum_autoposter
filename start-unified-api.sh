#!/bin/bash

# 統一 API 服務啟動腳本 - 簡化版本
echo "🚀 啟動 Forum Autoposter Unified API..."

# 設置環境變數
export PYTHONPATH="/app"
export PORT=${PORT:-8000}

echo "📋 環境變數:"
echo "  PORT: $PORT"
echo "  PYTHONPATH: $PYTHONPATH"

# 進入統一 API 目錄
cd "docker-container/finlab python/apps/unified-api"

# 檢查文件是否存在
if [ ! -f "main.py" ]; then
    echo "❌ 找不到 main.py 文件"
    ls -la
    exit 1
fi

echo "📁 當前目錄內容:"
ls -la

echo "📦 檢查依賴是否已安裝..."
pip list | grep fastapi || echo "⚠️ FastAPI 未安裝，嘗試安裝..."
pip install --no-cache-dir -r requirements.txt

# 啟動服務
echo "🌟 啟動統一 API 服務在端口 $PORT..."
exec uvicorn main:app --host 0.0.0.0 --port $PORT --log-level info