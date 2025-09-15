@echo off
REM n8n-migration 專案啟動腳本 (Windows)
REM 啟動後端 Docker 服務 + 前端本地開發

setlocal enabledelayedexpansion

REM 顏色定義 (Windows 10+)
for /f %%a in ('echo prompt $E ^| cmd') do set "ESC=%%a"
set "RED=%ESC%[31m"
set "GREEN=%ESC%[32m"
set "YELLOW=%ESC%[33m"
set "BLUE=%ESC%[34m"
set "NC=%ESC%[0m"

REM 日誌函數
:log_info
echo %BLUE%[INFO]%NC% %~1
goto :eof

:log_success
echo %GREEN%[SUCCESS]%NC% %~1
goto :eof

:log_warning
echo %YELLOW%[WARNING]%NC% %~1
goto :eof

:log_error
echo %RED%[ERROR]%NC% %~1
goto :eof

REM 檢查依賴
:check_dependencies
call :log_info "檢查系統依賴..."

REM 檢查 Docker
docker --version >nul 2>&1
if errorlevel 1 (
    call :log_error "Docker 未安裝或不在 PATH 中"
    exit /b 1
)
for /f "tokens=*" %%i in ('docker --version') do call :log_success "Docker 已安裝: %%i"

REM 檢查 Docker Compose
docker-compose --version >nul 2>&1
if errorlevel 1 (
    call :log_error "Docker Compose 未安裝或不在 PATH 中"
    exit /b 1
)
for /f "tokens=*" %%i in ('docker-compose --version') do call :log_success "Docker Compose 已安裝: %%i"

REM 檢查 Node.js
node --version >nul 2>&1
if errorlevel 1 (
    call :log_error "Node.js 未安裝或不在 PATH 中"
    exit /b 1
)
for /f "tokens=*" %%i in ('node --version') do call :log_success "Node.js 已安裝: %%i"

REM 檢查 npm
npm --version >nul 2>&1
if errorlevel 1 (
    call :log_error "npm 未安裝或不在 PATH 中"
    exit /b 1
)
for /f "tokens=*" %%i in ('npm --version') do call :log_success "npm 已安裝: %%i"

goto :eof

REM 停止現有服務
:stop_services
call :log_info "停止現有服務..."

REM 停止 Docker 服務
docker-compose -f docker-compose.full.yml ps -q >nul 2>&1
if not errorlevel 1 (
    docker-compose -f docker-compose.full.yml down
    call :log_success "Docker 服務已停止"
) else (
    call :log_info "沒有運行中的 Docker 服務"
)

REM 停止前端服務 (如果有的話)
tasklist /FI "IMAGENAME eq node.exe" /FI "WINDOWTITLE eq npm run dev*" >nul 2>&1
if not errorlevel 1 (
    taskkill /F /IM node.exe /FI "WINDOWTITLE eq npm run dev*" >nul 2>&1
    call :log_success "前端服務已停止"
)

goto :eof

REM 啟動後端服務
:start_backend
call :log_info "啟動後端 Docker 服務..."

REM 構建並啟動服務
docker-compose -f docker-compose.full.yml up -d --build

REM 等待服務啟動
call :log_info "等待服務啟動..."
timeout /t 10 /nobreak >nul

REM 檢查服務狀態
call :log_info "檢查服務狀態..."
docker-compose -f docker-compose.full.yml ps

call :log_success "後端服務啟動完成"
goto :eof

REM 安裝前端依賴
:install_frontend_deps
call :log_info "安裝前端依賴..."

set "frontend_dir=docker-container\finlab python\apps\dashboard-frontend"

if not exist "%frontend_dir%" (
    call :log_error "前端目錄不存在: %frontend_dir%"
    exit /b 1
)

cd /d "%frontend_dir%"

if not exist "package.json" (
    call :log_error "package.json 不存在"
    exit /b 1
)

REM 安裝依賴
npm install

cd /d "%~dp0"

call :log_success "前端依賴安裝完成"
goto :eof

REM 啟動前端服務
:start_frontend
call :log_info "啟動前端開發服務..."

set "frontend_dir=docker-container\finlab python\apps\dashboard-frontend"

cd /d "%frontend_dir%"

REM 設置環境變數
set "VITE_API_BASE_URL=http://localhost:8007"

call :log_info "前端服務將在 http://localhost:3000 啟動"
call :log_info "按 Ctrl+C 停止服務"

REM 啟動開發服務器
npm run dev

cd /d "%~dp0"
goto :eof

REM 顯示服務信息
:show_services
call :log_info "服務信息:"
echo.
echo 🔧 後端服務 (Docker):
echo   - PostgreSQL:     http://localhost:5432
echo   - Posting API:    http://localhost:8001
echo   - Revenue API:    http://localhost:8008
echo   - Dashboard API:  http://localhost:8007
echo   - Dashboard Backend: http://localhost:8012
echo   - Trending API:   http://localhost:8004
echo   - Summary API:    http://localhost:8003
echo   - Analyze API:    http://localhost:8002
echo   - OHLC API:       http://localhost:8005
echo   - Financial API:  http://localhost:8006
echo   - Monthly Revenue: http://localhost:8009
echo   - Fundamental Analyzer: http://localhost:8010
echo.
echo 🎨 前端服務 (本地):
echo   - Dashboard Frontend: http://localhost:3000
echo.
goto :eof

REM 主函數
:main
echo 🚀 n8n-migration 專案啟動腳本
echo ==================================
echo.

REM 檢查參數
if "%1"=="backend" goto :backend_only
if "%1"=="frontend" goto :frontend_only
if "%1"=="stop" goto :stop_only
if "%1"=="status" goto :status_only
if "%1"=="help" goto :help_only
if "%1"=="-h" goto :help_only
if "%1"=="--help" goto :help_only
if "%1"=="" goto :all_services
if "%1"=="all" goto :all_services

call :log_error "未知選項: %1"
echo 使用 'start.bat help' 查看可用選項
exit /b 1

:backend_only
call :check_dependencies
call :stop_services
call :start_backend
call :show_services
goto :end

:frontend_only
call :check_dependencies
call :install_frontend_deps
call :start_frontend
goto :end

:stop_only
call :stop_services
goto :end

:status_only
docker-compose -f docker-compose.full.yml ps
goto :end

:help_only
echo 用法: %0 [選項]
echo.
echo 選項:
echo   all       啟動所有服務 (默認)
echo   backend   只啟動後端 Docker 服務
echo   frontend  只啟動前端本地服務
echo   stop      停止所有服務
echo   status    查看服務狀態
echo   help      顯示此幫助信息
echo.
goto :end

:all_services
call :check_dependencies
call :stop_services
call :start_backend
call :install_frontend_deps
call :show_services
echo.
call :log_info "準備啟動前端服務..."
timeout /t 2 /nobreak >nul
call :start_frontend

:end
endlocal

