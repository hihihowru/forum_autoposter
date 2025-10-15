#!/bin/bash

# 服務停止腳本
# 用於一鍵停止所有後端服務

echo "🛑 停止所有後端服務..."

# 停止所有 uvicorn 進程
pkill -f uvicorn

# 等待進程完全停止
sleep 2

# 檢查是否還有進程在運行
if pgrep -f uvicorn > /dev/null; then
    echo "⚠️  強制停止剩餘進程..."
    pkill -9 -f uvicorn
fi

echo "✅ 所有服務已停止"
echo ""
echo "💡 使用 './start_services.sh' 重新啟動所有服務"



















