#!/bin/bash

# =============================================================================
# Git 檔案救援腳本 - 找出被 git restore 刪除/覆蓋的檔案
# 適用於 macOS + Cursor 編輯器環境
# =============================================================================

# 設定專案路徑（請自行修改）
PROJECT="."

# 檢查專案是否存在
if [ ! -d "$PROJECT" ]; then
    echo "❌ 錯誤：找不到專案資料夾 '$PROJECT'"
    echo "請修改腳本中的 PROJECT 變數為正確的專案名稱"
    exit 1
fi

# 建立輸出目錄
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
OUTPUT_DIR="n8n-migration-project_DIAG_${TIMESTAMP}"
mkdir -p "$OUTPUT_DIR"

echo "🔍 開始分析專案：$PROJECT"
echo "📁 輸出目錄：$OUTPUT_DIR"
echo ""

# =============================================================================
# 1. 記錄當前 Git 狀態
# =============================================================================
echo "📋 記錄當前 Git 狀態..."

git status > "$OUTPUT_DIR/git_status_now.txt" 2>&1
git ls-files > "$OUTPUT_DIR/git_tracked_now.txt" 2>&1
find . -type f -name "*.tsx" -o -name "*.ts" -o -name "*.jsx" -o -name "*.js" -o -name "*.py" -o -name "*.json" -o -name "*.md" | sort > "$OUTPUT_DIR/working_tree_now.txt"

echo "✅ Git 狀態已記錄"

# =============================================================================
# 2. 搜尋 Cursor Local History 中的檔案路徑
# =============================================================================
echo "🔍 搜尋 Cursor Local History..."

CURSOR_HISTORY_DIR="$HOME/Library/Application Support/Cursor/User/History"
HISTORY_PATHS_FILE="$OUTPUT_DIR/history_candidates_relative.txt"

# 清空輸出檔案
> "$HISTORY_PATHS_FILE"

if [ -d "$CURSOR_HISTORY_DIR" ]; then
    # 搜尋所有 entries.json 檔案
    find "$CURSOR_HISTORY_DIR" -name "entries.json" -exec cat {} \; 2>/dev/null | \
    grep -o '"resource":"file://[^"]*"' | \
    sed 's/"resource":"file:\/\/[^/]*//' | \
    sed 's/%20/ /g' | \
    sed 's/"//g' | \
    sort | uniq >> "$HISTORY_PATHS_FILE"
    
    echo "✅ 找到 $(wc -l < "$HISTORY_PATHS_FILE") 個歷史檔案路徑"
else
    echo "⚠️  Cursor History 目錄不存在"
fi

# =============================================================================
# 3. 搜尋專案內的備份檔案
# =============================================================================
echo "🔍 搜尋專案內備份檔案..."

# 搜尋各種備份檔案
find . -name ".history" -type d >> "$HISTORY_PATHS_FILE" 2>/dev/null
find . -name ".cursor" -type d >> "$HISTORY_PATHS_FILE" 2>/dev/null
find . -name ".vscode" -type d >> "$HISTORY_PATHS_FILE" 2>/dev/null
find . -name "*Autosaved*" >> "$HISTORY_PATHS_FILE" 2>/dev/null
find . -name "*.bak" >> "$HISTORY_PATHS_FILE" 2>/dev/null
find . -name "*.tmp" >> "$HISTORY_PATHS_FILE" 2>/dev/null
find . -name "*~" >> "$HISTORY_PATHS_FILE" 2>/dev/null

# 去重並排序
sort "$HISTORY_PATHS_FILE" | uniq > "${HISTORY_PATHS_FILE}.tmp" && mv "${HISTORY_PATHS_FILE}.tmp" "$HISTORY_PATHS_FILE"

echo "✅ 備份檔案搜尋完成"

# =============================================================================
# 4. 找出疑似被刪除的檔案
# =============================================================================
echo "🔍 分析疑似被刪除的檔案..."

MAYBE_DELETED_FILE="$OUTPUT_DIR/maybe_deleted_paths.txt"
> "$MAYBE_DELETED_FILE"

while IFS= read -r line; do
    # 清理路徑，移除專案路徑前綴
    clean_path=$(echo "$line" | sed "s|^.*$PROJECT/||" | sed "s|^/$PROJECT/||" | sed "s|^$PROJECT/||")
    
    # 檢查檔案是否存在
    if [ -n "$clean_path" ] && [ ! -f "$clean_path" ] && [ ! -d "$clean_path" ]; then
        echo "$clean_path" >> "$MAYBE_DELETED_FILE"
    fi
done < "$HISTORY_PATHS_FILE"

# 去重並排序
sort "$MAYBE_DELETED_FILE" | uniq > "${MAYBE_DELETED_FILE}.tmp" && mv "${MAYBE_DELETED_FILE}.tmp" "$MAYBE_DELETED_FILE"

echo "✅ 找到 $(wc -l < "$MAYBE_DELETED_FILE") 個疑似被刪除的檔案"

# =============================================================================
# 5. 找出疑似被覆蓋的檔案（近期修改頻繁）
# =============================================================================
echo "🔍 分析疑似被覆蓋的檔案..."

MAYBE_OVERWRITTEN_FILE="$OUTPUT_DIR/maybe_overwritten_paths.txt"
> "$MAYBE_OVERWRITTEN_FILE"

# 找出 14 天內修改的檔案
find . -type f \( -name "*.tsx" -o -name "*.ts" -o -name "*.jsx" -o -name "*.js" -o -name "*.py" -o -name "*.json" -o -name "*.md" \) -mtime -14 | \
sed 's|^\./||' | sort >> "$MAYBE_OVERWRITTEN_FILE"

# 去重並排序
sort "$MAYBE_OVERWRITTEN_FILE" | uniq > "${MAYBE_OVERWRITTEN_FILE}.tmp" && mv "${MAYBE_OVERWRITTEN_FILE}.tmp" "$MAYBE_OVERWRITTEN_FILE"

echo "✅ 找到 $(wc -l < "$MAYBE_OVERWRITTEN_FILE") 個疑似被覆蓋的檔案"

# =============================================================================
# 6. 生成分析報告
# =============================================================================
REPORT_FILE="$OUTPUT_DIR/analysis_report.txt"
> "$REPORT_FILE"

echo "Git 檔案救援分析報告" >> "$REPORT_FILE"
echo "生成時間：$(date)" >> "$REPORT_FILE"
echo "專案：$PROJECT" >> "$REPORT_FILE"
echo "===========================================" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

echo "📊 統計摘要：" >> "$REPORT_FILE"
echo "- 歷史檔案路徑總數：$(wc -l < "$HISTORY_PATHS_FILE")" >> "$REPORT_FILE"
echo "- 疑似被刪除檔案：$(wc -l < "$MAYBE_DELETED_FILE")" >> "$REPORT_FILE"
echo "- 疑似被覆蓋檔案：$(wc -l < "$MAYBE_OVERWRITTEN_FILE")" >> "$REPORT_FILE"
echo "- 當前工作目錄檔案：$(wc -l < "$OUTPUT_DIR/working_tree_now.txt")" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

echo "📁 輸出檔案說明：" >> "$REPORT_FILE"
echo "- maybe_deleted_paths.txt: 歷史中出現但目前不存在的檔案" >> "$REPORT_FILE"
echo "- maybe_overwritten_paths.txt: 目前存在但近期修改的檔案" >> "$REPORT_FILE"
echo "- history_candidates_relative.txt: 所有歷史檔案路徑" >> "$REPORT_FILE"
echo "- working_tree_now.txt: 當前專案中存在的檔案" >> "$REPORT_FILE"
echo "- git_status_now.txt: 當前 Git 狀態" >> "$REPORT_FILE"
echo "- git_tracked_now.txt: Git 追蹤的檔案清單" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

echo "🔧 還原建議：" >> "$REPORT_FILE"
echo "1. 在 Cursor 中按 Cmd+Shift+P，搜尋 'Local History'" >> "$REPORT_FILE"
echo "2. 開啟 'Local History: Find Entry to Restore'" >> "$REPORT_FILE"
echo "3. 根據 maybe_deleted_paths.txt 中的檔案名稱搜尋" >> "$REPORT_FILE"
echo "4. 選擇合適的時間點進行還原" >> "$REPORT_FILE"

cd ..

# =============================================================================
# 7. 完成
# =============================================================================
echo ""
echo "✅ 完成！請查看："
echo "   - maybe_deleted_paths.txt （疑似被刪）"
echo "   - maybe_overwritten_paths.txt （疑似被覆蓋）"
echo "   - analysis_report.txt （完整分析報告）"
echo ""
echo "📌 接下來建議："
echo "   1. 先查看 analysis_report.txt 了解整體情況"
echo "   2. 用 Cursor 的 Local History 功能還原 maybe_deleted_paths.txt 中的檔案"
echo "   3. 檢查 maybe_overwritten_paths.txt 中的檔案是否需要還原到更早版本"
echo ""
echo "📁 所有結果已儲存至：$OUTPUT_DIR"
