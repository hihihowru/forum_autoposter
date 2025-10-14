#!/bin/bash

# 手動發文功能整合啟動腳本

echo "🚀 啟動手動發文功能整合..."

# 檢查 Python 環境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安裝"
    exit 1
fi

# 檢查依賴套件
echo "📦 檢查依賴套件..."
python3 -c "import fastapi, uvicorn, sqlalchemy, pydantic" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📥 安裝依賴套件..."
    pip3 install fastapi uvicorn sqlalchemy pydantic psycopg2-binary
fi

# 檢查資料庫連接
echo "🔍 檢查資料庫連接..."
python3 -c "
import os
from sqlalchemy import create_engine
try:
    engine = create_engine('postgresql://postgres:password@localhost:5432/posting_management')
    engine.connect()
    print('✅ 資料庫連接正常')
except Exception as e:
    print(f'❌ 資料庫連接失敗: {e}')
    exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ 資料庫連接失敗，請檢查資料庫服務"
    exit 1
fi

# 檢查 stock_mapping.json
if [ ! -f "stock_mapping.json" ]; then
    echo "❌ 找不到 stock_mapping.json 文件"
    exit 1
fi

echo "✅ 環境檢查完成"

# 啟動 API 服務
echo "🌐 啟動手動發文 API 服務 (端口 8005)..."
python3 manual_posting_api.py &

# 等待服務啟動
sleep 3

# 檢查服務狀態
echo "🔍 檢查服務狀態..."
curl -s http://localhost:8005/api/manual-posting/health > /dev/null
if [ $? -eq 0 ]; then
    echo "✅ 手動發文 API 服務啟動成功"
    echo "📱 前端頁面: file://$(pwd)/manual_posting_page.html"
    echo "🔗 API 文檔: http://localhost:8005/docs"
    echo "🎯 Dashboard 整合: http://localhost:3000/posting-management/manual-posting"
    echo "⏹️  停止服務: pkill -f manual_posting_api.py"
else
    echo "❌ API 服務啟動失敗"
    exit 1
fi

# 運行測試
echo "🧪 運行測試..."
python3 test_manual_posting.py

echo ""
echo "🎉 手動發文功能整合完成！"
echo ""
echo "📋 使用說明:"
echo "1. 手動發文 API 服務已啟動 (端口 8005)"
echo "2. 前端頁面可直接使用: file://$(pwd)/manual_posting_page.html"
echo "3. Dashboard 整合頁面: http://localhost:3000/posting-management/manual-posting"
echo "4. 側邊欄導航: 發文管理 → 手動發文"
echo ""
echo "🔧 功能特點:"
echo "- 支援多 KOL 同時發文"
echo "- 股票選擇器 (2,263 個四位數股票)"
echo "- 熱門話題選擇器"
echo "- 多選功能"
echo "- 自動記錄到 post_records"
echo "- 即時搜尋"
echo "- 表單驗證"
echo ""
echo "📊 資料流程:"
echo "用戶輸入 → 前端驗證 → API 提交 → 後端處理 → 資料庫記錄 → 成功回應"

