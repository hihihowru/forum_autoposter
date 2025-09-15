#!/bin/bash

# n8n-migration 專案啟動腳本
# 啟動後端 Docker 服務 + 前端本地開發

set -e

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日誌函數
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 檢查依賴
check_dependencies() {
    log_info "檢查系統依賴..."
    
    # 檢查 Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安裝或不在 PATH 中"
        exit 1
    fi
    log_success "Docker 已安裝: $(docker --version)"
    
    # 檢查 Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose 未安裝或不在 PATH 中"
        exit 1
    fi
    log_success "Docker Compose 已安裝: $(docker-compose --version)"
    
    # 檢查 Node.js
    if ! command -v node &> /dev/null; then
        log_error "Node.js 未安裝或不在 PATH 中"
        exit 1
    fi
    log_success "Node.js 已安裝: $(node --version)"
    
    # 檢查 npm
    if ! command -v npm &> /dev/null; then
        log_error "npm 未安裝或不在 PATH 中"
        exit 1
    fi
    log_success "npm 已安裝: $(npm --version)"
}

# 停止現有服務
stop_services() {
    log_info "停止現有服務..."
    
    # 停止 Docker 服務
    if docker-compose -f docker-compose.full.yml ps -q | grep -q .; then
        docker-compose -f docker-compose.full.yml down
        log_success "Docker 服務已停止"
    else
        log_info "沒有運行中的 Docker 服務"
    fi
    
    # 停止前端服務 (如果有的話)
    if pgrep -f "npm run dev" > /dev/null; then
        pkill -f "npm run dev"
        log_success "前端服務已停止"
    fi
}

# 啟動後端服務
start_backend() {
    log_info "啟動後端 Docker 服務..."
    
    # 構建並啟動服務
    docker-compose -f docker-compose.full.yml up -d --build
    
    # 等待服務啟動
    log_info "等待服務啟動..."
    sleep 10
    
    # 檢查服務狀態
    log_info "檢查服務狀態..."
    docker-compose -f docker-compose.full.yml ps
    
    log_success "後端服務啟動完成"
}

# 安裝前端依賴
install_frontend_deps() {
    log_info "安裝前端依賴..."
    
    local frontend_dir="docker-container/finlab python/apps/dashboard-frontend"
    
    if [ ! -d "$frontend_dir" ]; then
        log_error "前端目錄不存在: $frontend_dir"
        exit 1
    fi
    
    cd "$frontend_dir"
    
    if [ ! -f "package.json" ]; then
        log_error "package.json 不存在"
        exit 1
    fi
    
    # 安裝依賴
    npm install
    
    cd - > /dev/null
    
    log_success "前端依賴安裝完成"
}

# 啟動前端服務
start_frontend() {
    log_info "啟動前端開發服務..."
    
    local frontend_dir="docker-container/finlab python/apps/dashboard-frontend"
    
    cd "$frontend_dir"
    
    # 設置環境變數
    export VITE_API_BASE_URL="http://localhost:8007"
    
    log_info "前端服務將在 http://localhost:3000 啟動"
    log_info "按 Ctrl+C 停止服務"
    
    # 啟動開發服務器
    npm run dev
    
    cd - > /dev/null
}

# 顯示服務信息
show_services() {
    log_info "服務信息:"
    echo ""
    echo "🔧 後端服務 (Docker):"
    echo "  - PostgreSQL:     http://localhost:5432"
    echo "  - Posting API:    http://localhost:8001"
    echo "  - Revenue API:    http://localhost:8008"
    echo "  - Dashboard API:  http://localhost:8007"
    echo "  - Dashboard Backend: http://localhost:8012"
    echo "  - Trending API:   http://localhost:8004"
    echo "  - Summary API:    http://localhost:8003"
    echo "  - Analyze API:    http://localhost:8002"
    echo "  - OHLC API:       http://localhost:8005"
    echo "  - Financial API:  http://localhost:8006"
    echo "  - Monthly Revenue: http://localhost:8009"
    echo "  - Fundamental Analyzer: http://localhost:8010"
    echo ""
    echo "🎨 前端服務 (本地):"
    echo "  - Dashboard Frontend: http://localhost:3000"
    echo ""
}

# 主函數
main() {
    echo "🚀 n8n-migration 專案啟動腳本"
    echo "=================================="
    echo ""
    
    # 檢查參數
    case "${1:-all}" in
        "backend")
            check_dependencies
            stop_services
            start_backend
            show_services
            ;;
        "frontend")
            check_dependencies
            install_frontend_deps
            start_frontend
            ;;
        "stop")
            stop_services
            ;;
        "status")
            docker-compose -f docker-compose.full.yml ps
            ;;
        "all"|"")
            check_dependencies
            stop_services
            start_backend
            install_frontend_deps
            show_services
            echo ""
            log_info "準備啟動前端服務..."
            sleep 2
            start_frontend
            ;;
        "help"|"-h"|"--help")
            echo "用法: $0 [選項]"
            echo ""
            echo "選項:"
            echo "  all       啟動所有服務 (默認)"
            echo "  backend   只啟動後端 Docker 服務"
            echo "  frontend  只啟動前端本地服務"
            echo "  stop      停止所有服務"
            echo "  status    查看服務狀態"
            echo "  help      顯示此幫助信息"
            echo ""
            ;;
        *)
            log_error "未知選項: $1"
            echo "使用 '$0 help' 查看可用選項"
            exit 1
            ;;
    esac
}

# 捕獲 Ctrl+C 信號
trap 'echo ""; log_info "正在停止服務..."; stop_services; exit 0' INT

# 執行主函數
main "$@"

