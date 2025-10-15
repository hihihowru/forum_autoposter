#!/bin/bash
# 841 排程監控腳本
TASK_ID='faf34317-f8c7-4abc-9b17-671433551661'
echo '🔍 開始監控 841 排程...'
echo '排程 ID: '
echo '下次執行時間: 2025-10-16 08:41:00 (台灣時間)'
echo '觸發器: 盤後漲停'
echo 'KOL: KOL-204'
echo '最大股票數: 1檔'
echo ''
echo '📊 當前狀態:'
curl -s http://localhost:8001/api/schedule/tasks | jq '.tasks[] | select(.task_id == "") | {status, run_count, success_count, last_run, next_run}' 2>/dev/null || echo 'API 暫時無法訪問'

