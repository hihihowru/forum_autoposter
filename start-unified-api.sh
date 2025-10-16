#!/bin/bash

# 統一 API 服務啟動腳本 - 最簡化版本
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

# 檢查 Python 和依賴
echo "🐍 Python 版本:"
python --version

echo "📦 檢查依賴..."
python -c "import fastapi; print('FastAPI version:', fastapi.__version__)" || {
    echo "❌ FastAPI 未安裝"
    pip install --no-cache-dir -r requirements.txt
}

python -c "import httpx; print('httpx version:', httpx.__version__)" || {
    echo "❌ httpx 未安裝，強制重新安裝所有依賴..."
    pip install --no-cache-dir --force-reinstall -r requirements.txt
}

# 啟動服務
echo "🌟 啟動統一 API 服務在端口 $PORT..."
echo "🔗 服務將在 http://0.0.0.0:$PORT 上運行"

# 使用 exec 確保正確的進程處理
exec python -m uvicorn main:app --host 0.0.0.0 --port $PORT --log-level info