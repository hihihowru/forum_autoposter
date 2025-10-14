#!/usr/bin/env bash
# restore_all_files.sh
# 從 Local History 還原 8:59 git restore 影響的所有檔案

set -euo pipefail

PROJECT_ROOT="/Users/williamchen/Documents/n8n-migration-project"
HISTORY_DIR="/Users/williamchen/Library/Application Support/Cursor/User/History"
BACKUP_DIR="$PROJECT_ROOT/RESTORE_BACKUP_$(date +%Y%m%d_%H%M%S)"
LOG_FILE="$PROJECT_ROOT/restore_all_log.txt"

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
    if [ "$size" -lt 50 ] || [ "$size" -gt 10000000 ]; then
        return 1
    fi
    
    # 檢查是否包含程式碼特徵
    if echo "$first_line" | grep -qE "(import|from|def |class |interface |export|function|#!/)"; then
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
    
    # 檢查是否為配置檔案
    if echo "$file" | grep -qE "\.(yml|yaml|json|md|sh|txt)$"; then
        return 0
    fi
    
    return 1
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
    log "開始還原 8:59 git restore 影響的所有檔案"
    log "專案目錄: $PROJECT_ROOT"
    log "歷史目錄: $HISTORY_DIR"
    log "備份目錄: $BACKUP_DIR"
    
    # 檢查必要目錄
    if [ ! -d "$HISTORY_DIR" ]; then
        error "找不到 Local History 目錄: $HISTORY_DIR"
        exit 1
    fi
    
    # 建立備份目錄
    mkdir -p "$BACKUP_DIR"
    
    # 統計變數
    local total_found=0
    local total_restored=0
    local total_skipped=0
    
    # 掃描所有歷史檔案
    log "掃描 Local History 檔案..."
    
    # 使用 Python 腳本來找出所有需要還原的檔案
    python3 << 'EOF'
import json
import datetime
import os
import urllib.parse
import subprocess
import sys

PROJECT_ROOT = "/Users/williamchen/Documents/n8n-migration-project"
HISTORY_DIR = "/Users/williamchen/Library/Application Support/Cursor/User/History"
target_date = datetime.date(2025, 10, 13)

# 8:59 附近的時間範圍
start_time = datetime.time(8, 55)
end_time = datetime.time(9, 5)

restore_files = []

print("掃描 Local History...")
for root, dirs, files in os.walk(HISTORY_DIR):
    if 'entries.json' in files:
        try:
            with open(os.path.join(root, 'entries.json'), 'r') as f:
                data = json.load(f)
            
            file_path = urllib.parse.unquote(data['resource'].replace('file://', ''))
            
            # 檢查 8:55-9:05 之間的記錄
            for entry in data['entries']:
                timestamp = entry['timestamp'] / 1000
                dt = datetime.datetime.fromtimestamp(timestamp)
                
                if dt.date() == target_date and start_time <= dt.time() <= end_time:
                    restore_files.append({
                        'file': file_path,
                        'entry_id': entry['id'],
                        'timestamp': dt,
                        'source': entry.get('source', 'Unknown'),
                        'history_dir': root
                    })
        except Exception as e:
            continue

# 按檔案分組，取最新的版本
file_groups = {}
for item in restore_files:
    file_name = os.path.basename(item['file'])
    if file_name not in file_groups:
        file_groups[file_name] = []
    file_groups[file_name].append(item)

# 為每個檔案找出最新版本
latest_versions = []
for file_name, versions in file_groups.items():
    # 按時間排序，取最新的
    latest = max(versions, key=lambda x: x['timestamp'])
    latest_versions.append(latest)

# 按時間排序
latest_versions.sort(key=lambda x: x['timestamp'])

print(f"找到 {len(latest_versions)} 個檔案需要還原")

# 輸出還原指令
for item in latest_versions:
    history_file = os.path.join(item['history_dir'], item['entry_id'])
    target_path = item['file']
    
    # 轉換為相對路徑
    if target_path.startswith(PROJECT_ROOT):
        target_path = os.path.relpath(target_path, PROJECT_ROOT)
    
    print(f"restore_file \"{history_file}\" \"{target_path}\"")
EOF
    
    # 執行還原
    log "開始執行還原..."
    
    # 重新掃描並還原
    python3 << 'EOF'
import json
import datetime
import os
import urllib.parse
import shutil

PROJECT_ROOT = "/Users/williamchen/Documents/n8n-migration-project"
HISTORY_DIR = "/Users/williamchen/Library/Application Support/Cursor/User/History"
BACKUP_DIR = f"{PROJECT_ROOT}/RESTORE_BACKUP_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
target_date = datetime.date(2025, 10, 13)

# 8:59 附近的時間範圍
start_time = datetime.time(8, 55)
end_time = datetime.time(9, 5)

restore_files = []

print("掃描 Local History...")
for root, dirs, files in os.walk(HISTORY_DIR):
    if 'entries.json' in files:
        try:
            with open(os.path.join(root, 'entries.json'), 'r') as f:
                data = json.load(f)
            
            file_path = urllib.parse.unquote(data['resource'].replace('file://', ''))
            
            # 檢查 8:55-9:05 之間的記錄
            for entry in data['entries']:
                timestamp = entry['timestamp'] / 1000
                dt = datetime.datetime.fromtimestamp(timestamp)
                
                if dt.date() == target_date and start_time <= dt.time() <= end_time:
                    restore_files.append({
                        'file': file_path,
                        'entry_id': entry['id'],
                        'timestamp': dt,
                        'source': entry.get('source', 'Unknown'),
                        'history_dir': root
                    })
        except Exception as e:
            continue

# 按檔案分組，取最新的版本
file_groups = {}
for item in restore_files:
    file_name = os.path.basename(item['file'])
    if file_name not in file_groups:
        file_groups[file_name] = []
    file_groups[file_name].append(item)

# 為每個檔案找出最新版本
latest_versions = []
for file_name, versions in file_groups.items():
    # 按時間排序，取最新的
    latest = max(versions, key=lambda x: x['timestamp'])
    latest_versions.append(latest)

# 按時間排序
latest_versions.sort(key=lambda x: x['timestamp'])

print(f"找到 {len(latest_versions)} 個檔案需要還原")

# 建立備份目錄
os.makedirs(BACKUP_DIR, exist_ok=True)

# 執行還原
restored_count = 0
skipped_count = 0

for item in latest_versions:
    history_file = os.path.join(item['history_dir'], item['entry_id'])
    target_path = item['file']
    
    try:
        # 檢查歷史檔案是否存在
        if not os.path.exists(history_file):
            print(f"⚠️  跳過: 歷史檔案不存在 {history_file}")
            skipped_count += 1
            continue
        
        # 檢查檔案大小
        file_size = os.path.getsize(history_file)
        if file_size < 50 or file_size > 10000000:
            print(f"⚠️  跳過: 檔案大小異常 {history_file} ({file_size} bytes)")
            skipped_count += 1
            continue
        
        # 備份現有檔案
        if os.path.exists(target_path):
            backup_path = os.path.join(BACKUP_DIR, os.path.relpath(target_path, PROJECT_ROOT))
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            shutil.copy2(target_path, backup_path)
            print(f"📁 備份: {target_path}")
        
        # 還原檔案
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        shutil.copy2(history_file, target_path)
        print(f"✅ 還原: {target_path} ({item['timestamp']})")
        restored_count += 1
        
    except Exception as e:
        print(f"❌ 錯誤: {target_path} - {e}")
        skipped_count += 1

print(f"\n🎉 還原完成!")
print(f"✅ 成功還原: {restored_count} 個檔案")
print(f"⚠️  跳過: {skipped_count} 個檔案")
print(f"📁 備份位置: {BACKUP_DIR}")
EOF
    
    log "還原完成!"
    success "詳細日誌: $LOG_FILE"
    
    echo
    echo "🎉 還原完成! 請檢查專案狀態。"
    echo "📁 備份位置: $BACKUP_DIR"
    echo "📋 詳細日誌: $LOG_FILE"
}

# 執行主函數
main "$@"



