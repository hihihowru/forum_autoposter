#!/bin/bash

# FinLab API 服務快速啟動腳本
# 用於快速啟動常用的服務組合

set -e

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 FinLab API 服務快速啟動${NC}"
echo ""

# 檢查 Docker 是否運行
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker 未運行，請先啟動 Docker${NC}"
    exit 1
fi

# 檢查 .env 文件
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ 找不到 .env 文件${NC}"
    echo "請確保 .env 文件存在並包含必要的 API 密鑰"
    exit 1
fi

echo -e "${GREEN}✅ Docker 運行正常${NC}"
echo -e "${GREEN}✅ .env 文件存在${NC}"
echo ""

# 選擇啟動模式
echo "請選擇啟動模式:"
echo "1) 核心服務 (推薦) - posting-service, ohlc-api, analyze-api, summary-api, trending-api, financial-api, dashboard-api"
echo "2) 完整服務 - 所有 API 服務"
echo "3) 開發模式 - 核心服務 + 儀表板"
echo "4) 自定義 - 手動選擇服務"
echo ""

read -p "請輸入選項 (1-4): " choice

case $choice in
    1)
        echo -e "${BLUE}啟動核心服務...${NC}"
        ./manage-services.sh start core
        ;;
    2)
        echo -e "${BLUE}啟動所有服務...${NC}"
        ./manage-services.sh start all
        ;;
    3)
        echo -e "${BLUE}啟動開發模式服務...${NC}"
        ./manage-services.sh start core
        ./manage-services.sh start dashboard
        ;;
    4)
        echo ""
        echo "可用服務組:"
        echo "- core (核心服務)"
        echo "- data (數據服務)"
        echo "- analysis (分析服務)"
        echo "- content (內容服務)"
        echo "- dashboard (儀表板服務)"
        echo "- training (訓練服務)"
        echo "- all (所有服務)"
        echo ""
        read -p "請輸入服務組名稱: " service_group
        ./manage-services.sh start "$service_group"
        ;;
    *)
        echo -e "${RED}無效選項${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}🎉 服務啟動完成！${NC}"
echo ""

# 等待服務啟動
echo -e "${YELLOW}等待服務啟動...${NC}"
sleep 5

# 檢查服務狀態
echo -e "${BLUE}檢查服務狀態:${NC}"
./manage-services.sh status

echo ""
echo -e "${BLUE}檢查服務健康狀態:${NC}"
./manage-services.sh health

echo ""
echo -e "${GREEN}✅ 啟動完成！${NC}"
echo ""
echo "常用命令:"
echo "  ./manage-services.sh status    - 查看服務狀態"
echo "  ./manage-services.sh health   - 檢查服務健康狀態"
echo "  ./manage-services.sh logs [服務名] - 查看服務日誌"
echo "  ./manage-services.sh stop all - 停止所有服務"
echo ""
