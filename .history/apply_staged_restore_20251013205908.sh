#!/bin/bash

# =============================================================================
# Git 檔案救援腳本 #2：套用暫存區檔案到專案並建立分支
# 使用方法：chmod +x apply_staged_restore.sh && ./apply_staged_restore.sh
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
APPLY_LIST_FILE="$RESTORE_STAGE_DIR/apply_list.txt"
BRANCH_NAME="recovered_work"

# 檢查 apply_list.txt 是否存在
if [ ! -f "$APPLY_LIST_FILE" ]; then
    echo "❌ 錯誤：找不到 apply_list.txt"
    echo "請在 $RESTORE_STAGE_DIR/ 目錄中建立 apply_list.txt"
    echo "格式：每行一個要還原的檔案路徑"
    echo ""
    echo "範例內容："
    echo "src/components/BatchHistoryPage.tsx"
    echo "src/components/ScheduleManagementPage.tsx"
    echo "src/components/ManualPostingPage.tsx"
    exit 1
fi

echo "🔧 開始套用檔案還原..."
echo "📁 暫存目錄：$RESTORE_STAGE_DIR"
echo "📋 套用清單：$APPLY_LIST_FILE"
echo "🌿 目標分支：$BRANCH_NAME"
echo ""

# 檢查 Git 狀態
if ! git status >/dev/null 2>&1; then
    echo "❌ 錯誤：當前目錄不是 Git 專案"
    exit 1
fi

# 建立或切換到目標分支
echo "🌿 建立/切換分支：$BRANCH_NAME"
if git show-ref --verify --quiet refs/heads/"$BRANCH_NAME"; then
    git checkout "$BRANCH_NAME"
    echo "✅ 已切換到現有分支：$BRANCH_NAME"
else
    git checkout -b "$BRANCH_NAME"
    echo "✅ 已建立新分支：$BRANCH_NAME"
fi

# 處理套用清單
TOTAL_FILES=$(wc -l < "$APPLY_LIST_FILE")
APPLIED_COUNT=0
FAILED_COUNT=0

echo ""
echo "📋 開始套用 $TOTAL_FILES 個檔案..."
echo ""

while IFS= read -r file_path; do
    if [ -z "$file_path" ]; then
        continue
    fi
    
    echo "🔧 套用：$file_path"
    
    # 檢查暫存區中是否有該檔案
    source_file="$RESTORE_STAGE_DIR/$file_path"
    
    if [ -f "$source_file" ]; then
        # 建立目標目錄
        target_dir="$(dirname "$file_path")"
        if [ "$target_dir" != "." ]; then
            mkdir -p "$target_dir"
        fi
        
        # 複製檔案
        cp "$source_file" "$file_path"
        
        if [ $? -eq 0 ]; then
            echo "  ✅ 已套用"
            APPLIED_COUNT=$((APPLIED_COUNT + 1))
        else
            echo "  ❌ 套用失敗"
            FAILED_COUNT=$((FAILED_COUNT + 1))
        fi
    else
        echo "  ❌ 找不到暫存檔案：$source_file"
        FAILED_COUNT=$((FAILED_COUNT + 1))
    fi
    
    echo ""
done < "$APPLY_LIST_FILE"

# 檢查是否有變更
if git diff --quiet; then
    echo "⚠️  沒有檔案變更，跳過 commit"
else
    echo "📝 準備提交變更..."
    
    # 顯示變更摘要
    echo "變更摘要："
    git diff --name-only
    echo ""
    
    # 詢問是否繼續
    read -p "是否要提交這些變更？(y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # 添加所有變更
        git add -A
        
        # 提交變更
        git commit -m "recover: restore work lost by git restore

- 還原 $APPLIED_COUNT 個檔案
- 來源：Cursor Local History
- 分支：$BRANCH_NAME
- 時間：$(date)"
        
        echo "✅ 已提交變更到分支：$BRANCH_NAME"
    else
        echo "❌ 已取消提交"
    fi
fi

# 生成總結報告
SUMMARY_FILE="$RESTORE_STAGE_DIR/apply_summary.txt"
cat > "$SUMMARY_FILE" << EOF
檔案套用總結報告
生成時間：$(date)
===========================================

📊 套用結果：
- 總檔案數：$TOTAL_FILES
- 成功套用：$APPLIED_COUNT
- 失敗：$FAILED_COUNT
- 成功率：$(( (APPLIED_COUNT * 100) / TOTAL_FILES ))%

🌿 Git 狀態：
- 當前分支：$BRANCH_NAME
- 變更狀態：$(git status --porcelain | wc -l | tr -d ' ') 個檔案

🔧 下一步：
1. 檢查還原的檔案是否正確
2. 測試功能是否正常
3. 如需合併到主分支：git checkout main && git merge $BRANCH_NAME
4. 如需放棄：git checkout main && git branch -D $BRANCH_NAME

⚠️  注意：
- 所有變更都在分支 $BRANCH_NAME 中
- 可以隨時切換回主分支
- 建議先測試後再合併
EOF

echo "✅ 套用完成！"
echo "📊 成功套用：$APPLIED_COUNT/$TOTAL_FILES 個檔案"
echo "🌿 當前分支：$BRANCH_NAME"
echo "📋 詳細報告：$SUMMARY_FILE"
echo ""
echo "🔧 下一步："
echo "   1. 檢查還原的檔案"
echo "   2. 測試功能"
echo "   3. 決定是否合併到主分支"


