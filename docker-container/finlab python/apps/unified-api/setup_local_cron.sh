#!/bin/bash
# Setup script for local hourly cronjob

echo "🔧 設置本地每小時任務 cronjob"
echo "================================"
echo ""

# Get Railway database URL
echo "📋 步驟 1: 獲取 Railway 數據庫 URL"
echo "運行以下命令獲取數據庫 URL:"
echo ""
echo "  cd '/Users/willchen/Documents/autoposter/forum_autoposter/docker-container/finlab python/apps/unified-api'"
echo "  railway variables --service forum_autoposter | grep DATABASE_URL"
echo ""
read -p "請複製完整的 DATABASE_URL 並貼上 (按 Enter 繼續): " DB_URL

if [ -z "$DB_URL" ]; then
    echo "❌ 未提供 DATABASE_URL，取消設置"
    exit 1
fi

# Create environment file
echo ""
echo "📝 步驟 2: 創建環境變數文件"
ENV_FILE="$HOME/.hourly_task_env"

cat > "$ENV_FILE" <<EOF
# Railway Database Connection
export DATABASE_URL="$DB_URL"
EOF

chmod 600 "$ENV_FILE"
echo "✅ 環境變數文件已創建: $ENV_FILE"

# Test the script
echo ""
echo "🧪 步驟 3: 測試腳本"
echo "運行測試..."

cd "/Users/willchen/Documents/autoposter/forum_autoposter/docker-container/finlab python/apps/unified-api"
source "$ENV_FILE"

python3 local_hourly_task.py

if [ $? -eq 0 ]; then
    echo "✅ 測試成功!"
else
    echo "❌ 測試失敗，請檢查錯誤訊息"
    exit 1
fi

# Setup cron job
echo ""
echo "⏰ 步驟 4: 設置 cronjob"
echo "準備添加 cronjob (每小時執行一次)..."
echo ""

CRON_CMD="0 * * * * source $ENV_FILE && cd '/Users/willchen/Documents/autoposter/forum_autoposter/docker-container/finlab python/apps/unified-api' && /usr/bin/python3 local_hourly_task.py >> /tmp/hourly_task.log 2>&1"

echo "將添加以下 cronjob:"
echo "$CRON_CMD"
echo ""

read -p "確認添加 cronjob? (y/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Add to crontab
    (crontab -l 2>/dev/null; echo "$CRON_CMD") | crontab -
    echo "✅ Cronjob 已添加"
    echo ""
    echo "查看當前 cronjob:"
    crontab -l
else
    echo "⏭️  跳過 cronjob 設置"
    echo ""
    echo "如需手動添加，運行:"
    echo "  crontab -e"
    echo ""
    echo "然後添加以下行:"
    echo "$CRON_CMD"
fi

echo ""
echo "================================"
echo "✅ 設置完成!"
echo ""
echo "📊 監控日誌:"
echo "  tail -f /tmp/hourly_task.log"
echo ""
echo "🔧 管理 cronjob:"
echo "  crontab -l    # 查看"
echo "  crontab -e    # 編輯"
echo "  crontab -r    # 刪除所有"
echo ""
