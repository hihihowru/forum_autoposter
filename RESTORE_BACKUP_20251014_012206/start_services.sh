#!/bin/bash

# 服務啟動腳本
# 用於一鍵啟動所有後端服務

echo "🚀 啟動所有後端服務..."

# 設置工作目錄
BASE_DIR="/Users/williamchen/Documents/n8n-migration-project/docker-container/finlab python/apps"

# 函數：啟動服務
start_service() {
    local service_name=$1
    local service_dir=$2
    local port=$3
    
    echo "📦 啟動 $service_name (端口: $port)..."
    cd "$BASE_DIR/$service_dir"
    
    # 檢查端口是否被占用
    if lsof -i :$port > /dev/null 2>&1; then
        echo "⚠️  端口 $port 已被占用，跳過 $service_name"
        return
    fi
    
    # 啟動服務
    python3 -m uvicorn main:app --host 0.0.0.0 --port $port --reload &
    echo "✅ $service_name 已啟動 (PID: $!)"
}

# 啟動所有服務
echo "🔧 啟動 posting-service..."
start_service "posting-service" "posting-service" "8001"

echo "📊 啟動 ohlc-api..."
start_service "ohlc-api" "ohlc-api" "8005"

echo "📈 啟動 analyze-api..."
start_service "analyze-api" "analyze-api" "8002"

echo "📝 啟動 summary-api..."
start_service "summary-api" "summary-api" "8003"

echo "🔥 啟動 trending-api..."
start_service "trending-api" "trending-api" "8004"

echo "📋 啟動 dashboard-api..."
start_service "dashboard-api" "dashboard-api" "8007"

echo "💰 啟動 financial-api..."
start_service "financial-api" "financial-api" "8006"

echo ""
echo "🎉 所有服務啟動完成！"
echo ""
echo "服務列表："
echo "  📦 posting-service:    http://localhost:8001"
echo "  📊 ohlc-api:          http://localhost:8005"
echo "  📈 analyze-api:       http://localhost:8002"
echo "  📝 summary-api:       http://localhost:8003"
echo "  🔥 trending-api:      http://localhost:8004"
echo "  📋 dashboard-api:     http://localhost:8007"
echo "  💰 financial-api:    http://localhost:8006"
echo ""
echo "💡 使用 'pkill -f uvicorn' 停止所有服務"
echo "💡 使用 'lsof -i :8001' 檢查特定端口"







