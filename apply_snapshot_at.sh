#!/usr/bin/env bash
# apply_snapshot_at.sh
# 功能：將 build_snapshot_at.sh 產生的快照檔案套回專案，並在 recovered_work 分支 commit

set -euo pipefail

PROJECT="${PROJECT:-n8n-migration-project}"   # "." 代表當前目錄
DIAG_DIR="${DIAG_DIR:-n8n-migration-project_DIAG_20251013_113216}"
TARGET_TS="${TARGET_TS:-2025-10-13 08:15:00}"

# 推導快照目錄
SNAP_TAG="$(echo "$TARGET_TS" | sed 's/[: ]/_/g' | sed 's/__/_/g')"
SNAP_DIR="$DIAG_DIR/RESTORE_SNAPSHOT_${SNAP_TAG}"
REPORT_MAP="$SNAP_DIR/report_map.csv"

if [ "$PROJECT" = "." ]; then
  PROJECT_ABS="$(pwd)"
else
  PROJECT_ABS="$(cd "$PROJECT" && pwd)"
fi

# 檢查
[ -d "$PROJECT_ABS/.git" ] || { echo "❌ $PROJECT_ABS 不是 Git 專案"; exit 1; }
[ -d "$SNAP_DIR" ] || { echo "❌ 找不到快照目錄：$SNAP_DIR（請先跑 build_snapshot_at.sh）"; exit 1; }
[ -s "$REPORT_MAP" ] || { echo "❌ $REPORT_MAP 無內容"; exit 1; }

cd "$PROJECT_ABS"

# 確保工作樹乾淨
if [ -n "$(git status --porcelain)" ]; then
  echo "❌ 工作樹不是乾淨狀態，請先 commit 或 stash 後再執行。"
  exit 1
fi

# 建立/切換分支
if git rev-parse --verify recovered_work >/dev/null 2>&1; then
  git checkout recovered_work
else
  git checkout -b recovered_work
fi

# 依報表逐檔覆蓋（report_map.csv 第1欄=相對路徑、第3欄=快照檔）
APPLIED=0
tail -n +2 "$REPORT_MAP" | while IFS=, read -r rel _ staged _; do
  [ -z "$rel" ] && continue
  src="$staged"
  # 去掉可能的空白
  rel="$(echo "$rel" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
  mkdir -p "$(dirname "$rel")"
  cp -p "$src" "$rel"
  echo "✔️ 套回：$rel"
  APPLIED=$((APPLIED+1))
done

git add -A
git commit -m "recover: snapshot at ${TARGET_TS}"

echo
echo "🎉 完成！已將 ${TARGET_TS} 的快照套回並提交於分支 recovered_work"
echo "👉 檢查差異：git diff main...recovered_work --stat"
echo "👉 備份到遠端：git push -u origin recovered_work"

