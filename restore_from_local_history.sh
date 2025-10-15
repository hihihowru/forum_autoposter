#!/bin/bash

# =============================================================================
# Git 檔案救援腳本 #1：從 Cursor Local History 還原檔案到暫存區
# 使用方法：chmod +x restore_from_local_history.sh && ./restore_from_local_history.sh
# 修改變數：DIAG_DIR (分析輸出資料夾名稱)
# =============================================================================

# 設定分析輸出資料夾（請修改為您的實際資料夾名稱）
DIAG_DIR="n8n-migration-project_DIAG_20251013_113216"

# 檢查資料夾是否存在
if [ ! -d "$DIAG_DIR" ]; then
    echo "❌ 錯誤：找不到分析資料夾 '$DIAG_DIR'"
    echo "請修改腳本中的 DIAG_DIR 變數為正確的資料夾名稱"
    exit 1
fi

# 設定路徑
RESTORE_STAGE_DIR="$DIAG_DIR/RESTORE_STAGE"
CURSOR_HISTORY_DIR="$HOME/Library/Application Support/Cursor/User/History"
REPORT_FILE="$RESTORE_STAGE_DIR/report_map.csv"
NOT_FOUND_FILE="$RESTORE_STAGE_DIR/not_found.txt"
SUMMARY_FILE="$RESTORE_STAGE_DIR/_SUMMARY.txt"

# 建立暫存目錄
mkdir -p "$RESTORE_STAGE_DIR"

echo "🔍 開始從 Cursor Local History 還原檔案..."
echo "📁 暫存目錄：$RESTORE_STAGE_DIR"
echo ""

# 清空輸出檔案
> "$REPORT_FILE"
> "$NOT_FOUND_FILE"

# 寫入 CSV 標題
echo "相對路徑,來源檔,暫存路徑,修改時間,檔案大小" > "$REPORT_FILE"

# 合併清單檔案
TEMP_LIST="$RESTORE_STAGE_DIR/temp_file_list.txt"
cat "$DIAG_DIR/maybe_deleted_paths.txt" "$DIAG_DIR/maybe_overwritten_paths.txt" 2>/dev/null | sort | uniq > "$TEMP_LIST"

TOTAL_FILES=$(wc -l < "$TEMP_LIST")
FOUND_COUNT=0
NOT_FOUND_COUNT=0

echo "📋 總共需要處理 $TOTAL_FILES 個檔案"
echo ""

# 處理每個檔案
while IFS= read -r file_path; do
    if [ -z "$file_path" ]; then
        continue
    fi
    
    echo "🔍 處理：$file_path"
    
    # 取得檔案名稱
    filename=$(basename "$file_path")
    
    # 在 Cursor History 中搜尋檔案
    found_files=()
    
    # 搜尋所有 entries.json 檔案
    if [ -d "$CURSOR_HISTORY_DIR" ]; then
        while IFS= read -r entry_file; do
            if [ -f "$entry_file" ]; then
                # 檢查是否包含目標檔案路徑
                if grep -q "$file_path" "$entry_file" 2>/dev/null; then
                    # 取得該 entry 的修改時間
                    mod_time=$(stat -f "%m" "$entry_file" 2>/dev/null || echo "0")
                    found_files+=("$entry_file|$mod_time")
                fi
            fi
        done < <(find "$CURSOR_HISTORY_DIR" -name "entries.json" 2>/dev/null)
    fi
    
    # 如果沒找到，嘗試搜尋檔案名稱
    if [ ${#found_files[@]} -eq 0 ]; then
        if [ -d "$CURSOR_HISTORY_DIR" ]; then
            while IFS= read -r entry_file; do
                if [ -f "$entry_file" ]; then
                    if grep -q "$filename" "$entry_file" 2>/dev/null; then
                        mod_time=$(stat -f "%m" "$entry_file" 2>/dev/null || echo "0")
                        found_files+=("$entry_file|$mod_time")
                    fi
                fi
            done < <(find "$CURSOR_HISTORY_DIR" -name "entries.json" 2>/dev/null)
        fi
    fi
    
    # 選擇最新的檔案
    if [ ${#found_files[@]} -gt 0 ]; then
        # 按修改時間排序，取最新的
        latest_entry=""
        latest_time=0
        
        for entry in "${found_files[@]}"; do
            entry_file=$(echo "$entry" | cut -d'|' -f1)
            entry_time=$(echo "$entry" | cut -d'|' -f2)
            
            if [ "$entry_time" -gt "$latest_time" ]; then
                latest_time="$entry_time"
                latest_entry="$entry_file"
            fi
        done
        
        # 從 entries.json 中提取檔案內容
        if [ -f "$latest_entry" ]; then
            # 嘗試從 JSON 中提取檔案內容
            temp_content=$(mktemp)
            
            # 使用 Python 解析 JSON 並提取檔案內容
            python3 -c "
import json
import sys
import os

try:
    with open('$latest_entry', 'r') as f:
        data = json.load(f)
    
    # 尋找包含目標路徑的資源
    target_path = '$file_path'
    target_filename = '$filename'
    
    for entry in data.get('entries', []):
        entry_id = entry.get('id', '')
        # 檢查是否有對應的檔案內容
        entry_dir = os.path.dirname('$latest_entry')
        content_file = os.path.join(entry_dir, entry_id)
        
        if os.path.exists(content_file):
            with open(content_file, 'r') as cf:
                content = cf.read()
                if target_path in content or target_filename in content:
                    print(content)
                    break
except:
    pass
" > "$temp_content" 2>/dev/null
            
            # 檢查是否有內容
            if [ -s "$temp_content" ]; then
                # 建立目標目錄
                target_dir="$RESTORE_STAGE_DIR/$(dirname "$file_path")"
                mkdir -p "$target_dir"
                
                # 處理重複檔名
                target_file="$RESTORE_STAGE_DIR/$file_path"
                counter=1
                while [ -f "$target_file" ]; do
                    target_file="${target_file%.*}.alt${counter}.${target_file##*.}"
                    counter=$((counter + 1))
                done
                
                # 複製檔案
                cp "$temp_content" "$target_file"
                
                # 取得檔案資訊
                file_size=$(stat -f "%z" "$target_file" 2>/dev/null || echo "0")
                mod_time_str=$(date -r "$latest_time" "+%Y-%m-%d %H:%M:%S" 2>/dev/null || echo "未知")
                
                # 記錄到 CSV
                echo "$file_path,$latest_entry,$target_file,$mod_time_str,$file_size" >> "$REPORT_FILE"
                
                echo "  ✅ 已還原到：$target_file"
                FOUND_COUNT=$((FOUND_COUNT + 1))
            else
                echo "$file_path" >> "$NOT_FOUND_FILE"
                echo "  ❌ 找不到內容"
                NOT_FOUND_COUNT=$((NOT_FOUND_COUNT + 1))
            fi
            
            rm -f "$temp_content"
        else
            echo "$file_path" >> "$NOT_FOUND_FILE"
            echo "  ❌ 找不到檔案"
            NOT_FOUND_COUNT=$((NOT_FOUND_COUNT + 1))
        fi
    else
        echo "$file_path" >> "$NOT_FOUND_FILE"
        echo "  ❌ 在 Local History 中找不到"
        NOT_FOUND_COUNT=$((NOT_FOUND_COUNT + 1))
    fi
    
    echo ""
done < "$TEMP_LIST"

# 生成總結報告
cat > "$SUMMARY_FILE" << EOF
Git 檔案救援總結報告
生成時間：$(date)
===========================================

📊 處理結果：
- 總檔案數：$TOTAL_FILES
- 成功還原：$FOUND_COUNT
- 找不到：$NOT_FOUND_COUNT
- 成功率：$(( (FOUND_COUNT * 100) / TOTAL_FILES ))%

📁 輸出檔案：
- report_map.csv：詳細還原記錄
- not_found.txt：找不到的檔案清單
- RESTORE_STAGE/：還原的檔案暫存區

🔧 下一步：
1. 檢查 RESTORE_STAGE/ 目錄中的檔案
2. 建立 apply_list.txt（一行一個要還原的檔案路徑）
3. 執行 apply_staged_restore.sh 套用還原

⚠️  注意：
- 所有檔案都已複製到暫存區，不會覆蓋原專案
- 請仔細檢查檔案內容後再決定是否套用
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

