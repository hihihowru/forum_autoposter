#!/bin/bash

# FinLab API 服務管理腳本
# 用於統一管理所有 API 服務的啟動、停止、重啟等操作

set -e

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 服務配置
COMPOSE_FILE="docker-compose.full.yml"
COMPOSE_FILE_CORE="docker-compose.yml"

# 服務分組
CORE_SERVICES="posting-service ohlc-api analyze-api summary-api trending-api financial-api dashboard-api"
DATA_SERVICES="revenue-api monthly-revenue-api"
ANALYSIS_SERVICES="fundamental-analyzer"
CONTENT_SERVICES="auto-publisher"
DASHBOARD_SERVICES="dashboard-backend dashboard-frontend"
TRAINING_SERVICES="trainer"

ALL_SERVICES="$CORE_SERVICES $DATA_SERVICES $ANALYSIS_SERVICES $CONTENT_SERVICES $DASHBOARD_SERVICES $TRAINING_SERVICES"

# 函數：顯示幫助信息
show_help() {
    echo -e "${BLUE}FinLab API 服務管理腳本${NC}"
    echo ""
    echo "用法: $0 [命令] [選項]"
    echo ""
    echo "命令:"
    echo "  start [服務組]    啟動服務"
    echo "  stop [服務組]     停止服務"
    echo "  restart [服務組]  重啟服務"
    echo "  status           顯示服務狀態"
    echo "  logs [服務名]    顯示服務日誌"
    echo "  health           檢查服務健康狀態"
    echo "  clean            清理停止的容器"
    echo "  rebuild [服務名] 重新構建服務"
    echo ""
    echo "服務組:"
    echo "  core             核心服務 (posting-service, ohlc-api, analyze-api, summary-api, trending-api, financial-api, dashboard-api)"
    echo "  data             數據服務 (revenue-api, monthly-revenue-api)"
    echo "  analysis         分析服務 (fundamental-analyzer)"
    echo "  content          內容服務 (auto-publisher)"
    echo "  dashboard        儀表板服務 (dashboard-backend, dashboard-frontend)"
    echo "  training         訓練服務 (trainer)"
    echo "  all              所有服務"
    echo ""
    echo "範例:"
    echo "  $0 start core          # 啟動核心服務"
    echo "  $0 stop all            # 停止所有服務"
    echo "  $0 restart posting-service  # 重啟特定服務"
    echo "  $0 logs ohlc-api       # 查看服務日誌"
    echo "  $0 health              # 檢查所有服務健康狀態"
}

# 函數：檢查 Docker Compose 文件
check_compose_file() {
    if [ ! -f "$COMPOSE_FILE" ]; then
        echo -e "${RED}錯誤: 找不到 $COMPOSE_FILE${NC}"
        echo "請確保在正確的目錄中運行此腳本"
        exit 1
    fi
}

# 函數：啟動服務
start_services() {
    local services="$1"
    echo -e "${GREEN}正在啟動服務: $services${NC}"
    
    if [ "$services" = "all" ]; then
        docker-compose -f "$COMPOSE_FILE" up -d
    else
        docker-compose -f "$COMPOSE_FILE" up -d $services
    fi
    
    echo -e "${GREEN}服務啟動完成${NC}"
}

# 函數：停止服務
stop_services() {
    local services="$1"
    echo -e "${YELLOW}正在停止服務: $services${NC}"
    
    if [ "$services" = "all" ]; then
        docker-compose -f "$COMPOSE_FILE" down
    else
        docker-compose -f "$COMPOSE_FILE" stop $services
    fi
    
    echo -e "${GREEN}服務停止完成${NC}"
}

# 函數：重啟服務
restart_services() {
    local services="$1"
    echo -e "${BLUE}正在重啟服務: $services${NC}"
    
    if [ "$services" = "all" ]; then
        docker-compose -f "$COMPOSE_FILE" restart
    else
        docker-compose -f "$COMPOSE_FILE" restart $services
    fi
    
    echo -e "${GREEN}服務重啟完成${NC}"
}

# 函數：顯示服務狀態
show_status() {
    echo -e "${BLUE}服務狀態:${NC}"
    docker-compose -f "$COMPOSE_FILE" ps
}

# 函數：顯示服務日誌
show_logs() {
    local service="$1"
    if [ -z "$service" ]; then
        echo -e "${RED}請指定服務名稱${NC}"
        echo "可用服務: $ALL_SERVICES"
        exit 1
    fi
    
    echo -e "${BLUE}顯示 $service 的日誌:${NC}"
    docker-compose -f "$COMPOSE_FILE" logs -f "$service"
}

# 函數：檢查服務健康狀態
check_health() {
    echo -e "${BLUE}檢查服務健康狀態:${NC}"
    echo ""
    
    # 檢查服務健康狀態的函數
    check_service_health() {
        local service="$1"
        local port="$2"
        
        if [ -n "$port" ]; then
            echo -n "檢查 $service (端口 $port): "
            if curl -s "http://localhost:$port/health" > /dev/null 2>&1; then
                echo -e "${GREEN}✅ 健康${NC}"
            else
                echo -e "${RED}❌ 不健康${NC}"
            fi
        else
            echo -e "${YELLOW}⚠️  $service: 無健康檢查端點${NC}"
        fi
    }
    
    # 檢查各個服務
    check_service_health "posting-service" "8001"
    check_service_health "analyze-api" "8002"
    check_service_health "summary-api" "8003"
    check_service_health "trending-api" "8004"
    check_service_health "ohlc-api" "8005"
    check_service_health "financial-api" "8006"
    check_service_health "dashboard-api" "8007"
    check_service_health "revenue-api" "8008"
    check_service_health "monthly-revenue-api" "8009"
    check_service_health "fundamental-analyzer" "8010"
    check_service_health "auto-publisher" "8011"
    check_service_health "dashboard-backend" "8012"
    check_service_health "dashboard-frontend" "3000"
    check_service_health "trainer" "8013"
}

# 函數：清理停止的容器
clean_containers() {
    echo -e "${YELLOW}清理停止的容器...${NC}"
    docker-compose -f "$COMPOSE_FILE" down --remove-orphans
    docker system prune -f
    echo -e "${GREEN}清理完成${NC}"
}

# 函數：重新構建服務
rebuild_service() {
    local service="$1"
    if [ -z "$service" ]; then
        echo -e "${RED}請指定服務名稱${NC}"
        echo "可用服務: $ALL_SERVICES"
        exit 1
    fi
    
    echo -e "${BLUE}重新構建服務: $service${NC}"
    docker-compose -f "$COMPOSE_FILE" down "$service"
    docker-compose -f "$COMPOSE_FILE" up -d --build "$service"
    echo -e "${GREEN}服務 $service 重新構建完成${NC}"
}

# 主邏輯
main() {
    check_compose_file
    
    case "$1" in
        "start")
            case "$2" in
                "core") start_services "$CORE_SERVICES" ;;
                "data") start_services "$DATA_SERVICES" ;;
                "analysis") start_services "$ANALYSIS_SERVICES" ;;
                "content") start_services "$CONTENT_SERVICES" ;;
                "dashboard") start_services "$DASHBOARD_SERVICES" ;;
                "training") start_services "$TRAINING_SERVICES" ;;
                "all") start_services "all" ;;
                "") start_services "$CORE_SERVICES" ;;
                *) start_services "$2" ;;
            esac
            ;;
        "stop")
            case "$2" in
                "core") stop_services "$CORE_SERVICES" ;;
                "data") stop_services "$DATA_SERVICES" ;;
                "analysis") stop_services "$ANALYSIS_SERVICES" ;;
                "content") stop_services "$CONTENT_SERVICES" ;;
                "dashboard") stop_services "$DASHBOARD_SERVICES" ;;
                "training") stop_services "$TRAINING_SERVICES" ;;
                "all") stop_services "all" ;;
                "") stop_services "$CORE_SERVICES" ;;
                *) stop_services "$2" ;;
            esac
            ;;
        "restart")
            case "$2" in
                "core") restart_services "$CORE_SERVICES" ;;
                "data") restart_services "$DATA_SERVICES" ;;
                "analysis") restart_services "$ANALYSIS_SERVICES" ;;
                "content") restart_services "$CONTENT_SERVICES" ;;
                "dashboard") restart_services "$DASHBOARD_SERVICES" ;;
                "training") restart_services "$TRAINING_SERVICES" ;;
                "all") restart_services "all" ;;
                "") restart_services "$CORE_SERVICES" ;;
                *) restart_services "$2" ;;
            esac
            ;;
        "status")
            show_status
            ;;
        "logs")
            show_logs "$2"
            ;;
        "health")
            check_health
            ;;
        "clean")
            clean_containers
            ;;
        "rebuild")
            rebuild_service "$2"
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            echo -e "${RED}未知命令: $1${NC}"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# 執行主函數
main "$@"
