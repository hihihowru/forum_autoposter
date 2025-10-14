#!/usr/bin/env bash
# 後援版：當 v3 以「檔名比對」抓不到時，改用「全文關鍵字」在 Cursor 目錄裡搜原始路徑字串
# 做法：
#  - 對每個相對路徑 rel，先 URL 解碼成 dec_rel
#  - 在 Cursor 目錄 grep "PROJECT_ABS/dec_rel" 文字，找出提到原始路徑的檔案（多半是 metadata / 索引）
#  - 從命中的資料夾取「最近修改」的檔案作為候選，複製到 RESTORE_STAGE/dec_rel
#  - 若同資料夾有多個候選，全部列到 alternatives.txt 給你挑

set -euo pipefail

PROJECT="${PROJECT:-n8n-migration-project}"  # 可設 PROJECT="." 表示目前資料夾
DIAG_DIR="${DIAG_DIR:-n8n-migration-project_DIAG_20251013_113216}"
LIMIT="${LIMIT:-50}"                          # 先小批次驗證，之後可改 0=不限
JOBS="${JOBS:-4}"

# 專案實際路徑
if [ "$PROJECT" = "." ]; then
  PROJECT_ABS="$(pwd)"
else
  PROJECT_ABS="$(cd "$PROJECT" && pwd)"
fi

APP_SUP="$HOME/Library/Application Support/Cursor"

STAGE_DIR="$DIAG_DIR/RESTORE_STAGE"
REPORT_MAP="$STAGE_DIR/report_map_fallback.csv"
NOT_FOUND="$STAGE_DIR/not_found_fallback.txt"
ALTS="$STAGE_DIR/alternatives_fallback.txt"
SUMMARY="$STAGE_DIR/_SUMMARY_fallback.txt"
mkdir -p "$STAGE_DIR"
echo "relative_path,source_hit,staged_target,mtime_iso,bytes,hit_dir" > "$REPORT_MAP"
: > "$NOT_FOUND"; : > "$ALTS"; : > "$SUMMARY"

DELETED_LIST="$DIAG_DIR/maybe_deleted_paths.txt"
OVER_LIST="$DIAG_DIR/maybe_overwritten_paths.txt"

# 合併清單
ALL="$STAGE_DIR/_all_targets_fb.txt"; : > "$ALL"
[ -f "$DELETED_LIST" ] && cat "$DELETED_LIST" >> "$ALL"
[ -f "$OVER_LIST" ] && cat "$OVER_LIST" >> "$ALL"
sort -u "$ALL" -o "$ALL"

# LIMIT
if [ "${LIMIT:-0}" -gt 0 ]; then
  head -n "$LIMIT" "$ALL" > "$ALL.tmp" && mv "$ALL.tmp" "$ALL"
fi

urldecode () {
  python3 - <<'PY' "$1"
import sys, urllib.parse
print(urllib.parse.unquote(sys.argv[1]))
PY
}

stat_iso ()  { stat -f "%Sm" -t "%Y-%m-%d %H:%M:%S" "$1" 2>/dev/null || date -r "$1" "+%Y-%m-%d %H:%M:%S" 2>/dev/null || echo "1970-01-01 00:00:00"; }
stat_size () { stat -f "%z" "$1" 2>/dev/null || stat -c "%s" "$1" 2>/dev/null || echo 0; }

process_one () {
  local rel="$1"
  [ -z "$rel" ] && return 0
  local dec_rel; dec_rel="$(urldecode "$rel")"

  echo "🔎 搜：$dec_rel" >&2

  # 在 Cursor 目錄全文搜尋「專案絕對路徑 + 相對路徑」這段字串
  local hits tmp_hits
  tmp_hits="$(mktemp)"
  if command -v rg >/dev/null 2>&1; then
    rg -n --hidden --no-mmap --glob '!*Cache*' --glob '!*GPUCache*' --glob '!*Code Cache*' \
       --fixed-strings "$PROJECT_ABS/$dec_rel" "$APP_SUP" 2>/dev/null | awk -F: '{print $1}' | sort -u > "$tmp_hits" || true
  else
    grep -Rsl --exclude-dir='*Cache*' --exclude-dir='*GPUCache*' --exclude-dir='*Code Cache*' \
         -- "$PROJECT_ABS/$dec_rel" "$APP_SUP" 2>/dev/null | sort -u > "$tmp_hits" || true
  fi

  if [ ! -s "$tmp_hits" ]; then
    echo "$rel" >> "$NOT_FOUND"
    rm -f "$tmp_hits"
    echo "  ❌ 無命中（找不到記錄路徑的 metadata）" >&2
    return 0
  fi

  # 對每個命中檔案，取其所在目錄，找該目錄內最近修改的檔案當候選
  local staged=0
  while IFS= read -r hit; do
    [ -f "$hit" ] || continue
    local dir; dir="$(dirname "$hit")"

    # 試著優先抓看起來像內容檔（不是 json/metadata），否則就抓目錄內最大/最新的檔
    local cand
    cand="$(find "$dir" -type f ! -name "*.json" ! -name "*.sqlite" -print0 2>/dev/null \
            | xargs -0 ls -t 2>/dev/null | head -n 1)"
    [ -z "$cand" ] && cand="$(ls -t "$dir"/* 2>/dev/null | head -n 1 || true)"
    [ -z "$cand" ] && continue

    local target="$STAGE_DIR/$dec_rel"
    mkdir -p "$(dirname "$target")"
    if [ -f "$target" ]; then
      target="${target}.$(date +%Y%m%d_%H%M%S).alt"
    fi
    cp -p "$cand" "$target" 2>/dev/null || continue

    local mtime size
    mtime="$(stat_iso "$cand")"
    size="$(stat_size "$cand")"
    echo "$rel,$hit,$target,$mtime,$size,$dir" >> "$REPORT_MAP"
    echo "  ✅ 暫存：$target  ←  命中：$hit" >&2
    staged=1

    # 額外列出同目錄其他候選
    local others
    others="$(ls -t "$dir"/* 2>/dev/null | tail -n +2 | head -n 5 || true)"
    if [ -n "$others" ]; then
      {
        echo "[$dec_rel] 其他候選（$dir）："
        echo "$others"
        echo
      } >> "$ALTS"
    fi

    # 命中一個目錄就先收手，避免重複
    break
  done < "$tmp_hits"

  [ "$staged" -eq 0 ] && echo "$rel" >> "$NOT_FOUND"
  rm -f "$tmp_hits"
}

export -f urldecode stat_iso stat_size process_one
export PROJECT_ABS APP_SUP STAGE_DIR REPORT_MAP NOT_FOUND ALTS

TOTAL=$(wc -l < "$ALL" | tr -d ' ')
echo "🚀 後援搜尋啟動（小批次 LIMIT=${LIMIT:-50}，並行 $JOBS）"
echo "📦 目標數：$TOTAL"
echo

# 平行處理
if command -v xargs >/dev/null 2>&1; then
  < "$ALL" xargs -I {} -P "$JOBS" bash -lc 'process_one "$@"' _ {}
else
  # 沒有 xargs 的極少數情況下，就序列處理
  while IFS= read -r rel; do process_one "$rel"; done < "$ALL"
fi

# 統計
FOUND=$(($(wc -l < "$REPORT_MAP")-1))
MISS=$(wc -l < "$NOT_FOUND" | awk '{print $1}')
{
  echo "總結（後援）"
  echo "----"
  echo "成功暫存：$FOUND"
  echo "未找到：$MISS"
  echo "報表：$REPORT_MAP"
  echo "未命中：$NOT_FOUND"
  echo "其他候選：$ALTS"
} > "$SUMMARY"

echo
echo "🎉 後援完成！成功：$FOUND，未找到：$MISS"
echo "📑 報表：$REPORT_MAP"
echo "⚠️ 未命中：$NOT_FOUND"
echo "🔁 其他候選：$ALTS"
echo "🧾 總結：$SUMMARY"

