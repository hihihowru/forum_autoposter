#!/usr/bin/env bash
# build_snapshot_at.sh
# 功能：根據目標時間點 TARGET_TS，從 Cursor Local History 建立「當時」的檔案快照
# 規則：對每個相對路徑，從索引中選擇 mtime<=TARGET_TS 的最新一個；若沒有，寫入 not_found_before.txt
# 並用「後援搜尋」嘗試用原始路徑字串抓到候選（同一資料夾內最新檔），最大化命中率。
# 只會輸出到 DIAG/RESTORE_SNAPSHOT_<ts>/ ，不會覆蓋專案。

set -euo pipefail

# ==== 參數（請依需要覆蓋）====
PROJECT="${PROJECT:-n8n-migration-project}"   # 用 "." 表示在專案根目錄執行
DIAG_DIR="${DIAG_DIR:-n8n-migration-project_DIAG_20251013_113216}"
TARGET_TS="${TARGET_TS:-2025-10-13 08:15:00}"  # 目標時間（本地時區，Asia/Taipei）
JOBS="${JOBS:-6}"
ONLY_DELETED="${ONLY_DELETED:-0}"             # 1=只處理被刪檔清單
LIMIT="${LIMIT:-0}"                            # 驗證用：只處理前 N 筆

# ==== 路徑判定 ====
if [ "$PROJECT" = "." ]; then
  PROJECT_ABS="$(pwd)"
else
  PROJECT_ABS="$(cd "$PROJECT" && pwd)"
fi

APP_SUP="$HOME/Library/Application Support/Cursor"
SNAP_TAG="$(echo "$TARGET_TS" | sed 's/[: ]/_/g' | sed 's/__/_/g')"
STAGE_DIR="$DIAG_DIR/RESTORE_SNAPSHOT_${SNAP_TAG}"
mkdir -p "$STAGE_DIR"

REPORT_MAP="$STAGE_DIR/report_map.csv"
NOT_FOUND="$STAGE_DIR/not_found.txt"
NOT_BEFORE="$STAGE_DIR/not_found_before.txt"  # 沒有<=目標時間的版本
ALTS="$STAGE_DIR/alternatives.txt"
SUMMARY="$STAGE_DIR/_SUMMARY.txt"
INDEX="$DIAG_DIR/RESTORE_STAGE/_cursor_history_index.tsv"  # 可重用 v3 的索引（若無會重建）

echo "relative_path,src,staged_target,mtime_iso,bytes,source_type" > "$REPORT_MAP"
: > "$NOT_FOUND"; : > "$NOT_BEFORE"; : > "$ALTS"; : > "$SUMMARY"

# ==== 時間處理（轉 epoch）====
# macOS BSD date 支援 -j -f；Linux 可用 GNU date -d。這裡優先用 python 可靠轉換。
TARGET_EPOCH="$(python3 - <<'PY' "$TARGET_TS"
import sys, datetime, time
# 直接以本地時區解讀（你在本機執行即為本地8:15）
ts=sys.argv[1]
dt=datetime.datetime.strptime(ts,"%Y-%m-%d %H:%M:%S")
print(int(dt.timestamp()))
PY
)"

# ==== 讀取清單 ====
DELETED_LIST="$DIAG_DIR/maybe_deleted_paths.txt"
OVER_LIST="$DIAG_DIR/maybe_overwritten_paths.txt"
ALL="$STAGE_DIR/_targets.txt"; : > "$ALL"
if [ "$ONLY_DELETED" = "1" ]; then
  [ -f "$DELETED_LIST" ] && cat "$DELETED_LIST" >> "$ALL"
else
  [ -f "$DELETED_LIST" ] && cat "$DELETED_LIST" >> "$ALL"
  [ -f "$OVER_LIST" ] && cat "$OVER_LIST" >> "$ALL"
fi
sort -u "$ALL" -o "$ALL"
if [ "$LIMIT" -gt 0 ]; then head -n "$LIMIT" "$ALL" > "$ALL.tmp" && mv "$ALL.tmp" "$ALL"; fi

# ==== 建立/讀取索引 ====
build_index () {
  local out="$1"; : > "$out"
  local roots=()
  [ -d "$APP_SUP/User/History" ] && roots+=("$APP_SUP/User/History")
  while IFS= read -r d; do roots+=("$d"); done < <(find "$APP_SUP/User/workspaceStorage" -type d -name History 2>/dev/null || true)
  roots+=("$APP_SUP")
  [ -d "$PROJECT_ABS/.history" ] && roots+=("$PROJECT_ABS/.history")
  [ -d "$PROJECT_ABS/.cursor" ] && roots+=("$PROJECT_ABS/.cursor")
  [ -d "$PROJECT_ABS/.vscode" ] && roots+=("$PROJECT_ABS/.vscode")

  echo "🧱 建立索引（第一次會久一點）..."
  for r in "${roots[@]}"; do
    [ -d "$r" ] || continue
    find "$r" -type f -print0 2>/dev/null | while IFS= read -r -d '' p; do
      base="$(basename "$p")"
      mt=$(stat -f "%m" "$p" 2>/dev/null || stat -c "%Y" "$p" 2>/dev/null || echo 0)
      sz=$(stat -f "%z" "$p" 2>/dev/null || stat -c "%s" "$p" 2>/dev/null || echo 0)
      printf "%s\t%s\t%s\t%s\n" "$mt" "$sz" "$p" "$base" >> "$out"
    done
  done
  sort -t $'\t' -k4,4 -k1,1nr "$out" -o "$out"
  echo "✅ 索引完成：$(wc -l < "$out" | tr -d ' ') 筆"
}

if [ ! -s "$INDEX" ]; then
  mkdir -p "$(dirname "$INDEX")"
  build_index "$INDEX"
else
  echo "📚 使用既有索引：$INDEX"
fi

# ==== 小工具 ====
urldecode () {
  python3 - <<'PY' "$1"
import sys, urllib.parse
print(urllib.parse.unquote(sys.argv[1]))
PY
}
stat_iso ()  { stat -f "%Sm" -t "%Y-%m-%d %H:%M:%S" "$1" 2>/dev/null || date -r "$1" "+%Y-%m-%d %H:%M:%S" 2>/dev/null || echo "1970-01-01 00:00:00"; }
stat_size () { stat -f "%z" "$1" 2>/dev/null || stat -c "%s" "$1" 2>/dev/null || echo 0; }
src_type () {
  case "$1" in
    *"/User/History/"*) echo "cursor_history" ;;
    *"/workspaceStorage/"*"/History/"*) echo "cursor_ws_history" ;;
    *"/.history/"*) echo "project_history" ;;
    *"/.cursor/"*) echo "project_cursor" ;;
    *"/.vscode/"*) echo "vscode_meta" ;;
    *"/Cache/"*) echo "cache" ;;
    *) echo "unknown" ;;
  esac
}

# 後援：用原始路徑全文搜索 metadata，從同資料夾抓最近檔案
fallback_fetch () {
  local dec_rel="$1"
  local hit tmp; tmp="$(mktemp)"
  if command -v rg >/dev/null 2>&1; then
    rg -n --hidden --no-mmap --glob '!*Cache*' --glob '!*GPUCache*' --glob '!*Code Cache*' \
       --fixed-strings "$PROJECT_ABS/$dec_rel" "$APP_SUP" 2>/dev/null \
       | awk -F: '{print $1}' | sort -u > "$tmp" || true
  else
    grep -Rsl --exclude-dir='*Cache*' --exclude-dir='*GPUCache*' --exclude-dir='*Code Cache*' \
         -- "$PROJECT_ABS/$dec_rel" "$APP_SUP" 2>/dev/null | sort -u > "$tmp" || true
  fi
  if [ ! -s "$tmp" ]; then rm -f "$tmp"; return 1; fi
  while IFS= read -r hit; do
    [ -f "$hit" ] || continue
    dir="$(dirname "$hit")"
    cand="$(ls -t "$dir"/* 2>/dev/null | head -n1 || true)"
    [ -n "$cand" ] || continue
    echo "$cand"
    rm -f "$tmp"
    return 0
  done < "$tmp"
  rm -f "$tmp"; return 1
}

# 單檔處理
process_one () {
  local rel="$1"; [ -z "$rel" ] && return 0
  local dec_rel; dec_rel="$(urldecode "$rel")"
  local base; base="$(basename "$dec_rel")"

  # 在索引中找 base 相同且 mtime<=TARGET_EPOCH 的第一筆
  local line
  line="$(awk -F'\t' -v b="$base" -v t="$TARGET_EPOCH" '$4==b && $1<=t {print; exit}' "$INDEX")"
  if [ -z "$line" ]; then
    # 沒有 <= 的版本，記錄一下，並嘗試後援
    echo "$rel" >> "$NOT_BEFORE"
    # 後援：用完整路徑字串在 Cursor 目錄全文搜
    if cand="$(fallback_fetch "$dec_rel")"; then
      src="$cand"
    else
      # 還是不行就宣告 not_found
      echo "$rel" >> "$NOT_FOUND"
      echo "  ❌ 找不到 <= $TARGET_TS 的版本：$dec_rel" >&2
      return 0
    fi
  else
    # 取出欄位：mtime size fullpath basename
    src="$(echo "$line" | awk -F'\t' '{print $3}')"
  fi

  # 複製到 SNAPSHOT 目錄
  target="$STAGE_DIR/$dec_rel"
  mkdir -p "$(dirname "$target")"
  if [ -f "$target" ]; then
    target="${target}.$(date +%Y%m%d_%H%M%S).alt"
  fi
  cp -p "$src" "$target" 2>/dev/null || { echo "$rel" >> "$NOT_FOUND"; return 0; }

  mtime="$(stat_iso "$src")"
  size="$(stat_size "$src")"
  echo "$dec_rel,$src,$target,$mtime,$size,$(src_type "$src")" >> "$REPORT_MAP"
  echo "  ✅ 暫存：$dec_rel  ←  $src" >&2
}

export -f urldecode stat_iso stat_size src_type fallback_fetch process_one
export PROJECT_ABS APP_SUP STAGE_DIR REPORT_MAP NOT_FOUND NOT_BEFORE ALTS TARGET_EPOCH TARGET_TS

TOTAL=$(wc -l < "$ALL" | tr -d ' ')
echo "🚀 建立「$TARGET_TS」快照"
echo "📦 目標數：$TOTAL（並行 $JOBS）"
echo

# 並行處理
if command -v xargs >/dev/null 2>&1; then
  < "$ALL" xargs -I {} -P "$JOBS" bash -lc 'process_one "$@"' _ {}
else
  while IFS= read -r rel; do process_one "$rel"; done < "$ALL"
fi

FOUND=$(($(wc -l < "$REPORT_MAP")-1))
MISS=$(wc -l < "$NOT_FOUND" | awk '{print $1}')
MISS_BEFORE=$(wc -l < "$NOT_BEFORE" | awk '{print $1}')
{
  echo "總結"
  echo "----"
  echo "目標時間：$TARGET_TS"
  echo "成功暫存：$FOUND"
  echo "找不到任何候選：$MISS"
  echo "沒有 <= 目標時間的版本（可改用稍後版本）：$MISS_BEFORE"
  echo "快照路徑：$STAGE_DIR"
} > "$SUMMARY"

echo
echo "🎉 完成！快照：$STAGE_DIR"
echo "📑 報表：$REPORT_MAP"
echo "⚠️ 無 <= 時間版本：$NOT_BEFORE"
echo "⚠️ 完全未命中：$NOT_FOUND"
echo "🧾 總結：$SUMMARY"

