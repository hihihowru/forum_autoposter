#!/bin/bash

# FinLab API 服務監控腳本
# 用於實時監控服務狀態和健康狀況

set -e

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 監控間隔（秒）
INTERVAL=30

echo -e "${BLUE}🔍 FinLab API 服務監控器${NC}"
echo "監控間隔: ${INTERVAL}秒"
echo "按 Ctrl+C 停止監控"
echo ""

while true; do
    clear
    echo -e "${BLUE}🔍 FinLab API 服務監控器 - $(date)${NC}"
    echo "=========================================="
    echo ""
    
    # 檢查服務狀態
    echo -e "${YELLOW}📊 服務狀態:${NC}"
    ./manage-services.sh status | grep -E "(Up|Down|Exited)"
    echo ""
    
    # 檢查健康狀態
    echo -e "${YELLOW}💚 健康檢查:${NC}"
    ./manage-services.sh health
    echo ""
    
    # 顯示系統資源使用
    echo -e "${YELLOW}💻 系統資源:${NC}"
    echo "CPU: $(top -l 1 | grep "CPU usage" | awk '{print $3}' | sed 's/%//')"
    echo "記憶體: $(top -l 1 | grep "PhysMem" | awk '{print $2}')"
    echo ""
    
    echo "下次檢查: $(date -v +${INTERVAL}S)"
    sleep $INTERVAL
done
