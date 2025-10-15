#!/bin/bash

# =============================================================================
# Git 檔案救援腳本 v3：從 Cursor Local History 還原檔案到暫存區（加速版）
# 使用方法：chmod +x restore_from_local_history_v3.sh && ./restore_from_local_history_v3.sh
# 環境變數：JOBS=6 LIMIT=100 ONLY_DELETED=1
# =============================================================================

# 設定變數
DIAG_DIR="n8n-migration-project_DIAG_20251013_113216"
PROJECT="."
JOBS=${JOBS:-6}
LIMIT=${LIMIT:-0}
ONLY_DELETED=${ONLY_DELETED:-0}

# 檢查資料夾是否存在
if [ ! -d "$DIAG_DIR" ]; then
    echo "❌ 錯誤：找不到分析資料夾 '$DIAG_DIR'"
    echo "請確認資料夾存在，或修改腳本中的 DIAG_DIR 變數"
    exit 1
fi

# 設定路徑
RESTORE_STAGE_DIR="$DIAG_DIR/RESTORE_STAGE"
CURSOR_BASE_DIR="$HOME/Library/Application Support/Cursor"
INDEX_FILE="$RESTORE_STAGE_DIR/_cursor_history_index.tsv"
REPORT_FILE="$RESTORE_STAGE_DIR/report_map.csv"
NOT_FOUND_FILE="$RESTORE_STAGE_DIR/not_found.txt"
SUMMARY_FILE="$RESTORE_STAGE_DIR/_SUMMARY.txt"

# 建立暫存目錄
mkdir -p "$RESTORE_STAGE_DIR"

echo "🚀 Git 檔案救援腳本 v3（加速版）"
echo "📁 暫存目錄：$RESTORE_STAGE_DIR"
echo "⚙️  並行數：$JOBS"
if [ "$LIMIT" -gt 0 ]; then
    echo "🔢 限制數量：$LIMIT"
fi
if [ "$ONLY_DELETED" -eq 1 ]; then
    echo "📋 僅處理被刪檔案"
fi
echo ""

# =============================================================================
# 步驟一：建立索引
# =============================================================================
if [ ! -f "$INDEX_FILE" ]; then
    echo "🔎 開始建立索引..."
    
    # 清空索引檔案
    > "$INDEX_FILE"
    
    # 搜尋範圍
    search_paths=(
        "$CURSOR_BASE_DIR/User/History"
        "$CURSOR_BASE_DIR/User/workspaceStorage"
        "$CURSOR_BASE_DIR/.cursor"
        ".history"
        ".cursor"
        ".vscode"
    )
    
    total_files=0
    
    for search_path in "${search_paths[@]}"; do
        if [ -d "$search_path" ]; then
            echo "  📂 掃描：$search_path"
            
            # 遞迴搜尋所有檔案
            while IFS= read -r file; do
                if [ -f "$file" ]; then
                    # 取得檔案資訊
                    mtime=$(stat -f "%m" "$file" 2>/dev/null || echo "0")
                    size=$(stat -f "%z" "$file" 2>/dev/null || echo "0")
                    basename=$(basename "$file")
                    
                    # 寫入索引（格式：mtime_epoch \t size \t fullpath \t basename）
                    echo -e "$mtime\t$size\t$file\t$basename" >> "$INDEX_FILE"
                    total_files=$((total_files + 1))
                fi
            done < <(find "$search_path" -type f 2>/dev/null)
        fi
    done
    
    # 排序索引（basename 升冪、mtime 降冪）
    sort -k4,4 -k1,1nr "$INDEX_FILE" > "${INDEX_FILE}.tmp" && mv "${INDEX_FILE}.tmp" "$INDEX_FILE"
    
    echo "✅ 索引完成，共 $total_files 筆"
    echo "📄 索引檔案：$INDEX_FILE"
else
    echo "✅ 索引已存在，直接重用"
    total_files=$(wc -l < "$INDEX_FILE")
    echo "📄 索引檔案：$INDEX_FILE（$total_files 筆）"
fi

echo ""

# =============================================================================
# 步驟二：根據偵測結果還原檔案
# =============================================================================

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
if [ "$ONLY_DELETED" -eq 1 ]; then
    cat "$DIAG_DIR/maybe_deleted_paths.txt" 2>/dev/null | sort | uniq > "$TEMP_LIST"
else
    cat "$DIAG_DIR/maybe_deleted_paths.txt" "$DIAG_DIR/maybe_overwritten_paths.txt" 2>/dev/null | sort | uniq > "$TEMP_LIST"
fi

TOTAL_FILES=$(wc -l < "$TEMP_LIST")
FOUND_COUNT=0
NOT_FOUND_COUNT=0

# 限制處理數量
if [ "$LIMIT" -gt 0 ] && [ "$TOTAL_FILES" -gt "$LIMIT" ]; then
    echo "🔢 限制處理數量：$LIMIT/$TOTAL_FILES"
    head -n "$LIMIT" "$TEMP_LIST" > "${TEMP_LIST}.limited"
    mv "${TEMP_LIST}.limited" "$TEMP_LIST"
    TOTAL_FILES="$LIMIT"
fi

echo "📋 開始處理 $TOTAL_FILES 個檔案..."
echo ""

# 清空輸出檔案
> "$REPORT_FILE"
> "$NOT_FOUND_FILE"

# 寫入 CSV 標題
echo "相對路徑,來源檔,暫存路徑,修改時間,檔案大小" > "$REPORT_FILE"

# 平行處理函數
process_file() {
    local file_path="$1"
    local index_file="$2"
    local restore_stage_dir="$3"
    local report_file="$4"
    local not_found_file="$5"
    
    if [ -z "$file_path" ]; then
        return
    fi
    
    echo "🔍 處理：$file_path"
    
    # URL 解碼檔案路徑
    decoded_path=$(url_decode "$file_path")
    filename=$(basename "$decoded_path")
    
    # 從索引中尋找相同 basename 的檔案
    candidate=$(grep -m1 "^[0-9]*	[0-9]*	.*	$filename$" "$index_file" 2>/dev/null)
    
    if [ -n "$candidate" ]; then
        # 解析候選檔案資訊
        mtime=$(echo "$candidate" | cut -f1)
        size=$(echo "$candidate" | cut -f2)
        source_file=$(echo "$candidate" | cut -f3)
        
        if [ -f "$source_file" ]; then
            # 建立目標目錄
            target_dir="$restore_stage_dir/$(dirname "$decoded_path")"
            mkdir -p "$target_dir"
            
            # 處理重複檔名
            target_file="$restore_stage_dir/$decoded_path"
            counter=1
            while [ -f "$target_file" ]; do
                target_file="${target_file%.*}.alt${counter}.${target_file##*.}"
                counter=$((counter + 1))
            done
            
            # 複製檔案
            cp "$source_file" "$target_file"
            
            if [ $? -eq 0 ]; then
                # 取得檔案資訊
                file_size=$(stat -f "%z" "$target_file" 2>/dev/null || echo "0")
                mod_time_str=$(date -r "$mtime" "+%Y-%m-%d %H:%M:%S" 2>/dev/null || echo "未知")
                
                # 記錄到 CSV
                echo "$decoded_path,$source_file,$target_file,$mod_time_str,$file_size" >> "$report_file"
                
                echo "  ✅ 已暫存：$target_file"
                echo "1"  # 成功標記
            else
                echo "  ❌ 複製失敗"
                echo "$file_path" >> "$not_found_file"
                echo "0"  # 失敗標記
            fi
        else
            echo "  ❌ 找不到 Local History 候選 → $filename"
            echo "$file_path" >> "$not_found_file"
            echo "0"  # 失敗標記
        fi
    else
        echo "  ❌ 找不到 Local History 候選 → $filename"
        echo "$file_path" >> "$not_found_file"
        echo "0"  # 失敗標記
    fi
}

# 匯出函數供平行處理使用
export -f process_file
export -f url_decode

# 使用 GNU parallel 或 xargs 進行平行處理
if command -v parallel >/dev/null 2>&1; then
    echo "⚡ 使用 GNU parallel 進行平行處理..."
    cat "$TEMP_LIST" | parallel -j "$JOBS" process_file {} "$INDEX_FILE" "$RESTORE_STAGE_DIR" "$REPORT_FILE" "$NOT_FOUND_FILE" | grep -c "1" | read FOUND_COUNT
    NOT_FOUND_COUNT=$((TOTAL_FILES - FOUND_COUNT))
else
    echo "⚡ 使用 xargs 進行平行處理..."
    cat "$TEMP_LIST" | xargs -n 1 -P "$JOBS" -I {} bash -c 'process_file "$@"' _ {} "$INDEX_FILE" "$RESTORE_STAGE_DIR" "$REPORT_FILE" "$NOT_FOUND_FILE" | grep -c "1" | read FOUND_COUNT
    NOT_FOUND_COUNT=$((TOTAL_FILES - FOUND_COUNT))
fi

# 生成總結報告
cat > "$SUMMARY_FILE" << EOF
Git 檔案救援總結報告 v3（加速版）
生成時間：$(date)
===========================================

📊 處理結果：
- 總檔案數：$TOTAL_FILES
- 成功還原：$FOUND_COUNT
- 找不到：$NOT_FOUND_COUNT
- 成功率：$(( (FOUND_COUNT * 100) / TOTAL_FILES ))%

⚙️ 執行參數：
- 並行數：$JOBS
- 限制數量：$LIMIT
- 僅處理被刪檔案：$ONLY_DELETED

📁 輸出檔案：
- report_map.csv：詳細還原記錄
- not_found.txt：找不到的檔案清單
- RESTORE_STAGE/：還原的檔案暫存區
- _cursor_history_index.tsv：索引檔案

🔧 下一步：
1. 檢查 RESTORE_STAGE/ 目錄中的檔案
2. 建立 apply_list.txt（一行一個要還原的檔案路徑）
3. 執行 apply_staged_restore.sh 套用還原

⚠️  注意：
- 所有檔案都已複製到暫存區，不會覆蓋原專案
- 請仔細檢查檔案內容後再決定是否套用
- 支援 URL 編碼檔名自動解碼
- 索引檔案可重用，加速後續執行
EOF

# 清理暫存檔案
rm -f "$TEMP_LIST"

echo ""
echo "✅ 還原完成！"
echo "📁 暫存目錄：$RESTORE_STAGE_DIR"
echo "📊 成功還原：$FOUND_COUNT/$TOTAL_FILES 個檔案"
echo "📋 詳細報告：$SUMMARY_FILE"
echo ""

# =============================================================================
# 三行教學
# =============================================================================
echo "🔧 使用教學："
echo "1️⃣ 先跑小批次驗證：LIMIT=100 ./restore_from_local_history_v3.sh"
echo "2️⃣ 全量執行：./restore_from_local_history_v3.sh"
echo "3️⃣ 檢查暫存結果：ls -la $RESTORE_STAGE_DIR/"

