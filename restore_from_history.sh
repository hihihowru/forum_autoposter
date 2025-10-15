#!/usr/bin/env bash
# restore_from_history.sh
# 功能：從 .history 目錄中找到 8:55 前的最後版本並還原
# 目標時間：2025-10-13 08:55:00 之前

set -euo pipefail

PROJECT_ROOT="/Users/williamchen/Documents/n8n-migration-project"
TARGET_TIME="20251013085500"  # 8:55 AM (格式: YYYYMMDDHHMMSS)
HISTORY_DIR="$PROJECT_ROOT/.history"
BACKUP_DIR="$PROJECT_ROOT/RESTORE_BACKUP_$(date +%Y%m%d_%H%M%S)"
LOG_FILE="$PROJECT_ROOT/restore_log.txt"

# 顏色輸出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}✅ $1${NC}" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}❌ $1${NC}" | tee -a "$LOG_FILE"
}

# 檢查是否為可執行的程式碼檔案
is_valid_code_file() {
    local file="$1"
    local size=$(stat -f "%z" "$file" 2>/dev/null || echo 0)
    local first_line=$(head -1 "$file" 2>/dev/null || echo "")
    
    # 檢查檔案大小（太小可能是日誌，太大可能是錯誤）
    if [ "$size" -lt 100 ] || [ "$size" -gt 10000000 ]; then
        return 1
    fi
    
    # 檢查是否包含程式碼特徵
    if echo "$first_line" | grep -qE "(import|from|def |class |interface |export|function)"; then
        return 0
    fi
    
    # 檢查是否為 TypeScript/React 檔案
    if echo "$file" | grep -qE "\.(tsx?|jsx?)$" && head -5 "$file" | grep -qE "(React|import.*from)"; then
        return 0
    fi
    
    # 檢查是否為 Python 檔案
    if echo "$file" | grep -qE "\.py$" && head -5 "$file" | grep -qE "(import|from|def |class )"; then
        return 0
    fi
    
    return 1
}

# 提取檔案路徑（去掉時間戳）
extract_file_path() {
    local history_file="$1"
    echo "$history_file" | sed -E 's/_[0-9]{14}\.(tsx?|jsx?|py)$/.\1/'
}

# 找到指定檔案在目標時間前的最後版本
find_latest_version() {
    local target_path="$1"
    local base_name=$(basename "$target_path")
    local dir_name=$(dirname "$target_path")
    local extension="${base_name##*.}"
    
    # 在 .history 中尋找所有相關檔案
    local candidates=()
    while IFS= read -r -d '' file; do
        # 提取時間戳
        local timestamp=$(echo "$file" | grep -oE '_[0-9]{14}\.' | sed 's/[_.]//g')
        if [ -n "$timestamp" ] && [ "$timestamp" -lt "$TARGET_TIME" ]; then
            candidates+=("$timestamp:$file")
        fi
    done < <(find "$HISTORY_DIR" -name "*${base_name%.*}*" -type f -print0)
    
    # 按時間戳排序，取最新的
    if [ ${#candidates[@]} -gt 0 ]; then
        printf '%s\n' "${candidates[@]}" | sort -t: -k1 -nr | head -1 | cut -d: -f2-
    fi
}

# 還原單個檔案
restore_file() {
    local history_file="$1"
    local target_path="$2"
    
    if ! is_valid_code_file "$history_file"; then
        warning "跳過無效檔案: $history_file"
        return 1
    fi
    
    # 備份現有檔案
    if [ -f "$target_path" ]; then
        mkdir -p "$BACKUP_DIR/$(dirname "$target_path")"
        cp "$target_path" "$BACKUP_DIR/$target_path"
        log "備份現有檔案: $target_path"
    fi
    
    # 還原檔案
    mkdir -p "$(dirname "$target_path")"
    cp "$history_file" "$target_path"
    success "還原: $target_path"
    return 0
}

# 主函數
main() {
    log "開始還原程序 - 目標時間: 2025-10-13 08:55:00 之前"
    log "專案目錄: $PROJECT_ROOT"
    log "歷史目錄: $HISTORY_DIR"
    log "備份目錄: $BACKUP_DIR"
    
    # 檢查必要目錄
    if [ ! -d "$HISTORY_DIR" ]; then
        error "找不到 .history 目錄: $HISTORY_DIR"
        exit 1
    fi
    
    # 建立備份目錄
    mkdir -p "$BACKUP_DIR"
    
    # 統計變數
    local total_found=0
    local total_restored=0
    local total_skipped=0
    
    # 掃描所有歷史檔案
    log "掃描歷史檔案..."
    while IFS= read -r -d '' history_file; do
        total_found=$((total_found + 1))
        
        # 提取目標路徑
        local target_path=$(extract_file_path "$history_file")
        target_path="${target_path#.history/}"  # 移除 .history/ 前綴
        
        # 找到該檔案在目標時間前的最後版本
        local latest_version=$(find_latest_version "$target_path")
        
        if [ -n "$latest_version" ] && [ "$latest_version" = "$history_file" ]; then
            if restore_file "$history_file" "$target_path"; then
                total_restored=$((total_restored + 1))
            else
                total_skipped=$((total_skipped + 1))
            fi
        fi
    done < <(find "$HISTORY_DIR" -type f \( -name "*.tsx" -o -name "*.ts" -o -name "*.py" \) -print0)
    
    # 輸出統計
    log "還原完成!"
    success "總共找到: $total_found 個歷史檔案"
    success "成功還原: $total_restored 個檔案"
    warning "跳過: $total_skipped 個檔案"
    log "備份位置: $BACKUP_DIR"
    log "詳細日誌: $LOG_FILE"
    
    echo
    echo "🎉 還原完成! 請檢查專案狀態。"
    echo "📁 備份位置: $BACKUP_DIR"
    echo "📋 詳細日誌: $LOG_FILE"
}

# 執行主函數
main "$@"
