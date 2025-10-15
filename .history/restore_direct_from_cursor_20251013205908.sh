#!/bin/bash

# =============================================================================
# 直接從 Cursor Local History 還原檔案（快速版）
# 使用方法：chmod +x restore_direct_from_cursor.sh && ./restore_direct_from_cursor.sh
# =============================================================================

set -euo pipefail

DIAG_DIR="n8n-migration-project_DIAG_20251013_113216"
RESTORE_DIR="$DIAG_DIR/RESTORE_DIRECT"
CURSOR_HISTORY="$HOME/Library/Application Support/Cursor/User/History"

mkdir -p "$RESTORE_DIR"

echo "🚀 直接從 Cursor Local History 還原檔案"
echo "📁 還原目錄：$RESTORE_DIR"
echo ""

# URL 解碼函數
urldecode() {
    python3 -c "import urllib.parse; print(urllib.parse.unquote('$1'))"
}

# 處理單個檔案
process_file() {
    local encoded_path="$1"
    local decoded_path=$(urldecode "$encoded_path")
    local filename=$(basename "$decoded_path")
    
    echo "🔍 處理：$decoded_path"
    
    # 在 Cursor History 中搜尋檔案
    local found_files=()
    
    # 搜尋所有可能的檔案
    while IFS= read -r entry_dir; do
        if [ -d "$entry_dir" ]; then
            # 檢查 entries.json
            if [ -f "$entry_dir/entries.json" ]; then
                # 從 entries.json 中提取檔案內容
                python3 -c "
import json
import os
import sys

try:
    with open('$entry_dir/entries.json', 'r') as f:
        data = json.load(f)
    
    target_filename = '$filename'
    decoded_path = '$decoded_path'
    
    for entry in data.get('entries', []):
        entry_id = entry.get('id', '')
        content_file = os.path.join('$entry_dir', entry_id)
        
        if os.path.exists(content_file):
            with open(content_file, 'r', encoding='utf-8', errors='ignore') as cf:
                content = cf.read()
                # 檢查是否包含目標檔案內容
                if target_filename in content or decoded_path in content:
                    print(content_file)
                    break
except:
    pass
" | while read -r content_file; do
                    if [ -f "$content_file" ]; then
                        found_files+=("$content_file")
                    fi
                done
            fi
            
            # 直接搜尋檔案內容
            find "$entry_dir" -type f -name "*.tsx" -o -name "*.ts" -o -name "*.jsx" -o -name "*.js" -o -name "*.py" -o -name "*.md" 2>/dev/null | while read -r file; do
                if grep -q "$filename" "$file" 2>/dev/null || grep -q "$decoded_path" "$file" 2>/dev/null; then
                    found_files+=("$file")
                fi
            done
        fi
    done < <(find "$CURSOR_HISTORY" -type d 2>/dev/null)
    
    # 選擇最新的檔案
    if [ ${#found_files[@]} -gt 0 ]; then
        local latest_file=""
        local latest_time=0
        
        for file in "${found_files[@]}"; do
            if [ -f "$file" ]; then
                local mtime=$(stat -f "%m" "$file" 2>/dev/null || echo "0")
                if [ "$mtime" -gt "$latest_time" ]; then
                    latest_time="$mtime"
                    latest_file="$file"
                fi
            fi
        done
        
        if [ -n "$latest_file" ] && [ -f "$latest_file" ]; then
            # 建立目標目錄
            local target_dir="$RESTORE_DIR/$(dirname "$decoded_path")"
            mkdir -p "$target_dir"
            
            # 複製檔案
            local target_file="$RESTORE_DIR/$decoded_path"
            cp "$latest_file" "$target_file"
            
            if [ $? -eq 0 ]; then
                echo "  ✅ 已還原：$target_file"
                echo "1"  # 成功標記
            else
                echo "  ❌ 複製失敗"
                echo "0"  # 失敗標記
            fi
        else
            echo "  ❌ 找不到有效檔案"
            echo "0"  # 失敗標記
        fi
    else
        echo "  ❌ 在 Local History 中找不到"
        echo "0"  # 失敗標記
    fi
}

export -f process_file
export -f urldecode

# 讀取檔案清單
TEMP_LIST="$RESTORE_DIR/temp_list.txt"
cat "$DIAG_DIR/maybe_deleted_paths.txt" "$DIAG_DIR/maybe_overwritten_paths.txt" 2>/dev/null | sort | uniq > "$TEMP_LIST"

TOTAL_FILES=$(wc -l < "$TEMP_LIST")
FOUND_COUNT=0

echo "📋 開始處理 $TOTAL_FILES 個檔案..."
echo ""

# 處理檔案
while IFS= read -r file_path; do
    if [ -n "$file_path" ]; then
        result=$(process_file "$file_path")
        if [ "$result" = "1" ]; then
            FOUND_COUNT=$((FOUND_COUNT + 1))
        fi
    fi
done < "$TEMP_LIST"

# 生成報告
SUMMARY_FILE="$RESTORE_DIR/_SUMMARY.txt"
cat > "$SUMMARY_FILE" << EOF
直接還原總結報告
生成時間：$(date)
===========================================

📊 處理結果：
- 總檔案數：$TOTAL_FILES
- 成功還原：$FOUND_COUNT
- 失敗：$((TOTAL_FILES - FOUND_COUNT))
- 成功率：$(( (FOUND_COUNT * 100) / TOTAL_FILES ))%

📁 還原目錄：$RESTORE_DIR

🔧 下一步：
1. 檢查還原的檔案內容
2. 手動複製需要的檔案到專案
3. 測試功能是否正常
EOF

# 清理
rm -f "$TEMP_LIST"

echo ""
echo "✅ 直接還原完成！"
echo "📁 還原目錄：$RESTORE_DIR"
echo "📊 成功還原：$FOUND_COUNT/$TOTAL_FILES 個檔案"
echo "📋 詳細報告：$SUMMARY_FILE"
echo ""
echo "🔧 下一步："
echo "   1. 檢查 $RESTORE_DIR/ 目錄中的檔案"
echo "   2. 手動複製需要的檔案到專案"
echo "   3. 測試功能是否正常"


