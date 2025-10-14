#!/bin/bash

# =============================================================================
# 快速還原腳本 - 只處理最重要的檔案
# =============================================================================

set -euo pipefail

DIAG_DIR="n8n-migration-project_DIAG_20251013_113216"
RESTORE_DIR="$DIAG_DIR/RESTORE_QUICK"
CURSOR_HISTORY="$HOME/Library/Application Support/Cursor/User/History"

mkdir -p "$RESTORE_DIR"

echo "🚀 快速還原最重要的檔案"
echo "📁 還原目錄：$RESTORE_DIR"
echo ""

# 重點檔案清單（只處理這些）
KEY_FILES=(
    "BatchHistoryPage.tsx"
    "ScheduleManagementPage.tsx" 
    "ManualPostingPage.tsx"
    "SelfLearningPage.tsx"
    "InteractionAnalysis.tsx"
    "ScheduleConfigModal.tsx"
    "KOLDetail.tsx"
    "ContentManagement.tsx"
)

# URL 解碼函數
urldecode() {
    python3 -c "import urllib.parse; print(urllib.parse.unquote('$1'))"
}

# 快速搜尋函數
quick_search() {
    local filename="$1"
    echo "🔍 搜尋：$filename"
    
    # 在 Cursor History 中快速搜尋
    local found_file=""
    local latest_time=0
    
    # 只搜尋最近的幾個目錄
    find "$CURSOR_HISTORY" -type d -name "*" -mtime -7 2>/dev/null | head -20 | while read -r dir; do
        if [ -d "$dir" ]; then
            # 搜尋檔案內容
            find "$dir" -type f \( -name "*.tsx" -o -name "*.ts" -o -name "*.jsx" -o -name "*.js" \) 2>/dev/null | while read -r file; do
                if grep -q "$filename" "$file" 2>/dev/null; then
                    local mtime=$(stat -f "%m" "$file" 2>/dev/null || echo "0")
                    if [ "$mtime" -gt "$latest_time" ]; then
                        latest_time="$mtime"
                        found_file="$file"
                    fi
                fi
            done
        fi
    done
    
    if [ -n "$found_file" ] && [ -f "$found_file" ]; then
        # 複製檔案
        cp "$found_file" "$RESTORE_DIR/$filename"
        echo "  ✅ 已還原：$filename"
        return 0
    else
        echo "  ❌ 找不到：$filename"
        return 1
    fi
}

# 處理重點檔案
FOUND_COUNT=0
TOTAL_FILES=${#KEY_FILES[@]}

for filename in "${KEY_FILES[@]}"; do
    if quick_search "$filename"; then
        FOUND_COUNT=$((FOUND_COUNT + 1))
    fi
    echo ""
done

# 生成報告
SUMMARY_FILE="$RESTORE_DIR/_SUMMARY.txt"
cat > "$SUMMARY_FILE" << EOF
快速還原總結報告
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

echo "✅ 快速還原完成！"
echo "📁 還原目錄：$RESTORE_DIR"
echo "📊 成功還原：$FOUND_COUNT/$TOTAL_FILES 個檔案"
echo "📋 詳細報告：$SUMMARY_FILE"
echo ""
echo "🔧 下一步："
echo "   1. 檢查 $RESTORE_DIR/ 目錄中的檔案"
echo "   2. 手動複製需要的檔案到專案"
echo "   3. 測試功能是否正常"


