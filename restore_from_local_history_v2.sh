#!/bin/bash

# =============================================================================
# Git 檔案救援腳本 v2：從 Cursor Local History 還原檔案到暫存區
# 使用方法：chmod +x restore_from_local_history_v2.sh && ./restore_from_local_history_v2.sh
# 修改變數：DIAG_DIR (分析輸出資料夾名稱)
# =============================================================================

# 設定分析輸出資料夾
DIAG_DIR="n8n-migration-project_DIAG_20251013_113216"

# 檢查資料夾是否存在
if [ ! -d "$DIAG_DIR" ]; then
    echo "❌ 錯誤：找不到分析資料夾 '$DIAG_DIR'"
    echo "請確認資料夾存在，或修改腳本中的 DIAG_DIR 變數"
    exit 1
fi

# 設定路徑
RESTORE_STAGE_DIR="$DIAG_DIR/RESTORE_STAGE"
CURSOR_BASE_DIR="$HOME/Library/Application Support/Cursor"
REPORT_FILE="$RESTORE_STAGE_DIR/report_map.csv"
NOT_FOUND_FILE="$RESTORE_STAGE_DIR/not_found.txt"
ALTERNATIVES_FILE="$RESTORE_STAGE_DIR/alternatives.txt"
SUMMARY_FILE="$RESTORE_STAGE_DIR/_SUMMARY.txt"

# 建立暫存目錄
mkdir -p "$RESTORE_STAGE_DIR"

echo "🔍 開始從 Cursor Local History 還原檔案..."
echo "📁 暫存目錄：$RESTORE_STAGE_DIR"
echo ""

# 清空輸出檔案
> "$REPORT_FILE"
> "$NOT_FOUND_FILE"
> "$ALTERNATIVES_FILE"

# 寫入 CSV 標題
echo "相對路徑,來源檔,暫存路徑,修改時間,檔案大小" > "$REPORT_FILE"

# URL 解碼函數
url_decode() {
    echo "$1" | python3 -c "
import sys
import urllib.parse
for line in sys.stdin:
    print(urllib.parse.unquote(line.strip()))
"
}

# 合併清單檔案
TEMP_LIST="$RESTORE_STAGE_DIR/temp_file_list.txt"
cat "$DIAG_DIR/maybe_deleted_paths.txt" "$DIAG_DIR/maybe_overwritten_paths.txt" 2>/dev/null | sort | uniq > "$TEMP_LIST"

TOTAL_FILES=$(wc -l < "$TEMP_LIST")
FOUND_COUNT=0
NOT_FOUND_COUNT=0
ALTERNATIVES_COUNT=0

echo "📋 總共需要處理 $TOTAL_FILES 個檔案"
echo ""

# 處理每個檔案
while IFS= read -r file_path; do
    if [ -z "$file_path" ]; then
        continue
    fi
    
    echo "🔍 處理：$file_path"
    
    # URL 解碼檔案路徑
    decoded_path=$(url_decode "$file_path")
    filename=$(basename "$decoded_path")
    
    # 搜尋候選檔案
    candidates=()
    
    # 搜尋範圍
    search_paths=(
        "$CURSOR_BASE_DIR/User/History"
        "$CURSOR_BASE_DIR/User/workspaceStorage"
        "$CURSOR_BASE_DIR/.cursor"
        ".history"
        ".cursor"
        ".vscode"
    )
    
    # 在每個搜尋路徑中尋找檔案
    for search_path in "${search_paths[@]}"; do
        if [ -d "$search_path" ]; then
            # 搜尋 entries.json 檔案
            while IFS= read -r entry_file; do
                if [ -f "$entry_file" ]; then
                    # 檢查是否包含目標檔案路徑
                    if grep -q "$file_path" "$entry_file" 2>/dev/null || grep -q "$decoded_path" "$entry_file" 2>/dev/null || grep -q "$filename" "$entry_file" 2>/dev/null; then
                        # 取得該 entry 的修改時間
                        mod_time=$(stat -f "%m" "$entry_file" 2>/dev/null || echo "0")
                        candidates+=("$entry_file|$mod_time")
                    fi
                fi
            done < <(find "$search_path" -name "entries.json" 2>/dev/null)
            
            # 搜尋實際檔案內容
            while IFS= read -r content_file; do
                if [ -f "$content_file" ]; then
                    # 檢查檔案內容是否包含目標路徑或檔名
                    if grep -q "$file_path" "$content_file" 2>/dev/null || grep -q "$decoded_path" "$content_file" 2>/dev/null || grep -q "$filename" "$content_file" 2>/dev/null; then
                        mod_time=$(stat -f "%m" "$content_file" 2>/dev/null || echo "0")
                        candidates+=("$content_file|$mod_time")
                    fi
                fi
            done < <(find "$search_path" -type f \( -name "*.tsx" -o -name "*.ts" -o -name "*.jsx" -o -name "*.js" -o -name "*.py" -o -name "*.json" -o -name "*.md" \) 2>/dev/null)
        fi
    done
    
    # 選擇最新的檔案
    if [ ${#candidates[@]} -gt 0 ]; then
        # 按修改時間排序，取最新的
        latest_file=""
        latest_time=0
        
        for candidate in "${candidates[@]}"; do
            candidate_file=$(echo "$candidate" | cut -d'|' -f1)
            candidate_time=$(echo "$candidate" | cut -d'|' -f2)
            
            if [ "$candidate_time" -gt "$latest_time" ]; then
                latest_time="$candidate_time"
                latest_file="$candidate_file"
            fi
        done
        
        # 嘗試從檔案中提取內容
        if [ -f "$latest_file" ]; then
            # 檢查是否為 entries.json
            if [[ "$latest_file" == *"entries.json" ]]; then
                # 從 JSON 中提取檔案內容
                temp_content=$(mktemp)
                
                python3 -c "
import json
import sys
import os

try:
    with open('$latest_file', 'r') as f:
        data = json.load(f)
    
    # 尋找包含目標路徑的資源
    target_path = '$file_path'
    decoded_path = '$decoded_path'
    target_filename = '$filename'
    
    for entry in data.get('entries', []):
        entry_id = entry.get('id', '')
        # 檢查是否有對應的檔案內容
        entry_dir = os.path.dirname('$latest_file')
        content_file = os.path.join(entry_dir, entry_id)
        
        if os.path.exists(content_file):
            with open(content_file, 'r', encoding='utf-8', errors='ignore') as cf:
                content = cf.read()
                if target_path in content or decoded_path in content or target_filename in content:
                    print(content)
                    break
except Exception as e:
    pass
" > "$temp_content" 2>/dev/null
                
                # 檢查是否有內容
                if [ -s "$temp_content" ]; then
                    content_source="$temp_content"
                else
                    rm -f "$temp_content"
                    content_source="$latest_file"
                fi
            else
                content_source="$latest_file"
            fi
            
            # 建立目標目錄
            target_dir="$RESTORE_STAGE_DIR/$(dirname "$decoded_path")"
            mkdir -p "$target_dir"
            
            # 處理重複檔名
            target_file="$RESTORE_STAGE_DIR/$decoded_path"
            counter=1
            while [ -f "$target_file" ]; do
                target_file="${target_file%.*}.alt${counter}.${target_file##*.}"
                counter=$((counter + 1))
            done
            
            # 複製檔案
            cp "$content_source" "$target_file"
            
            if [ $? -eq 0 ]; then
                # 取得檔案資訊
                file_size=$(stat -f "%z" "$target_file" 2>/dev/null || echo "0")
                mod_time_str=$(date -r "$latest_time" "+%Y-%m-%d %H:%M:%S" 2>/dev/null || echo "未知")
                
                # 記錄到 CSV
                echo "$decoded_path,$latest_file,$target_file,$mod_time_str,$file_size" >> "$REPORT_FILE"
                
                echo "  ✅ 已暫存：$target_file"
                FOUND_COUNT=$((FOUND_COUNT + 1))
                
                # 記錄替代選項
                if [ ${#candidates[@]} -gt 1 ]; then
                    echo "$decoded_path: ${#candidates[@]} 個候選檔案" >> "$ALTERNATIVES_FILE"
                    ALTERNATIVES_COUNT=$((ALTERNATIVES_COUNT + 1))
                fi
            else
                echo "$file_path" >> "$NOT_FOUND_FILE"
                echo "  ❌ 複製失敗"
                NOT_FOUND_COUNT=$((NOT_FOUND_COUNT + 1))
            fi
            
            # 清理暫存檔案
            if [ -n "$temp_content" ] && [ -f "$temp_content" ]; then
                rm -f "$temp_content"
            fi
        else
            echo "$file_path" >> "$NOT_FOUND_FILE"
            echo "  ❌ 找不到檔案"
            NOT_FOUND_COUNT=$((NOT_FOUND_COUNT + 1))
        fi
    else
        echo "$file_path" >> "$NOT_FOUND_FILE"
        echo "  ❌ 找不到候選檔"
        NOT_FOUND_COUNT=$((NOT_FOUND_COUNT + 1))
    fi
    
    echo ""
done < "$TEMP_LIST"

# 生成總結報告
cat > "$SUMMARY_FILE" << EOF
Git 檔案救援總結報告 v2
生成時間：$(date)
===========================================

📊 處理結果：
- 總檔案數：$TOTAL_FILES
- 成功還原：$FOUND_COUNT
- 找不到：$NOT_FOUND_COUNT
- 有替代選項：$ALTERNATIVES_COUNT
- 成功率：$(( (FOUND_COUNT * 100) / TOTAL_FILES ))%

📁 輸出檔案：
- report_map.csv：詳細還原記錄
- not_found.txt：找不到的檔案清單
- alternatives.txt：有多個候選的檔案
- RESTORE_STAGE/：還原的檔案暫存區

🔧 下一步：
1. 檢查 RESTORE_STAGE/ 目錄中的檔案
2. 建立 apply_list.txt（一行一個要還原的檔案路徑）
3. 執行 apply_staged_restore.sh 套用還原

⚠️  注意：
- 所有檔案都已複製到暫存區，不會覆蓋原專案
- 請仔細檢查檔案內容後再決定是否套用
- 支援 URL 編碼檔名自動解碼
EOF

# 清理暫存檔案
rm -f "$TEMP_LIST"

echo "✅ 還原完成！"
echo "📁 暫存目錄：$RESTORE_STAGE_DIR"
echo "📊 成功還原：$FOUND_COUNT/$TOTAL_FILES 個檔案"
echo "📋 詳細報告：$SUMMARY_FILE"
echo ""
echo "🔧 下一步："
echo "   1. 檢查 RESTORE_STAGE/ 目錄中的檔案"
echo "   2. 建立 apply_list.txt"
echo "   3. 執行 apply_staged_restore.sh"

