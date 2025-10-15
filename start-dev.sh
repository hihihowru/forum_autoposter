#!/bin/bash

# 開發環境啟動腳本
# 用途：啟動後端服務，前端需要手動啟動

echo "🚀 啟動 n8n-migration 開發環境..."

# 檢查 Docker 是否運行
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker 未運行，請先啟動 Docker"
    exit 1
fi

# 停止現有服務
echo "🛑 停止現有服務..."
docker-compose -f docker-compose.dev.yml down

# 啟動後端服務
echo "🔧 啟動後端服務..."
docker-compose -f docker-compose.dev.yml up -d

# 等待服務啟動
echo "⏳ 等待服務啟動..."
sleep 10

# 檢查服務狀態
echo "📊 檢查服務狀態..."
docker-compose -f docker-compose.dev.yml ps

echo ""
echo "✅ 後端服務已啟動！"
echo ""
echo "📋 服務列表："
echo "  - dashboard-api: http://localhost:8007"
echo "  - trending-api: http://localhost:8004"
echo "  - posting-service: http://localhost:8001"
echo "  - postgres-db: localhost:5432"
echo ""
echo "🎯 下一步："
echo "  1. 啟動前端：cd docker-container/finlab\\ python/apps/dashboard-frontend && npm run dev"
echo "  2. 訪問前端：http://localhost:3000"
echo ""
echo "🔧 管理命令："
echo "  - 查看日誌：docker-compose -f docker-compose.dev.yml logs -f [service-name]"
echo "  - 停止服務：docker-compose -f docker-compose.dev.yml down"
echo "  - 重啟服務：docker-compose -f docker-compose.dev.yml restart [service-name]"
