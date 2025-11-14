#!/bin/bash
# Setup cronjob for hourly CMoney article reaction task
# This script will automatically configure cron to run the hourly task

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PYTHON_PATH="/usr/bin/python3"
LOG_FILE="$HOME/Library/Logs/cmoney_hourly_task.log"
ENV_FILE="$HOME/.hourly_task_env"

echo "======================================================================"
echo "🚀 Setting up CMoney Hourly Reaction Bot Cronjob"
echo "======================================================================"
echo ""

# Check if python3 exists
if ! command -v python3 &> /dev/null; then
    echo "❌ python3 not found. Please install Python 3 first."
    exit 1
fi

PYTHON_PATH=$(which python3)
echo "✅ Found Python: $PYTHON_PATH"

# Check if env file exists
if [ ! -f "$ENV_FILE" ]; then
    echo "❌ Environment file not found: $ENV_FILE"
    echo "💡 Please create it with:"
    echo "   export DATABASE_URL='postgresql://postgres:PASSWORD@HOST:PORT/railway'"
    exit 1
fi

echo "✅ Found environment file: $ENV_FILE"

# Check if script exists
SCRIPT_PATH="$SCRIPT_DIR/local_hourly_task.py"
if [ ! -f "$SCRIPT_PATH" ]; then
    echo "❌ Script not found: $SCRIPT_PATH"
    exit 1
fi

echo "✅ Found script: $SCRIPT_PATH"

# Create log directory if it doesn't exist
mkdir -p "$(dirname "$LOG_FILE")"
echo "✅ Log directory ready: $(dirname "$LOG_FILE")"

# Create the cron command
CRON_CMD="0 * * * * source $ENV_FILE && cd \"$SCRIPT_DIR\" && $PYTHON_PATH \"$SCRIPT_PATH\" >> \"$LOG_FILE\" 2>&1"

echo ""
echo "======================================================================"
echo "📋 Cronjob Configuration:"
echo "======================================================================"
echo "Schedule: Every hour at minute 0 (0 * * * *)"
echo "Script:   $SCRIPT_PATH"
echo "Python:   $PYTHON_PATH"
echo "Log file: $LOG_FILE"
echo "Env file: $ENV_FILE"
echo ""

# Check if crontab already has this entry
if crontab -l 2>/dev/null | grep -q "local_hourly_task.py"; then
    echo "⚠️  Cronjob already exists for local_hourly_task.py"
    echo ""
    read -p "Do you want to replace it? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Cancelled. Existing cronjob unchanged."
        exit 0
    fi

    # Remove old entry
    crontab -l 2>/dev/null | grep -v "local_hourly_task.py" | crontab -
    echo "🗑️  Removed old cronjob entry"
fi

# Add new cron job
(crontab -l 2>/dev/null; echo "$CRON_CMD") | crontab -

echo ""
echo "======================================================================"
echo "✅ Cronjob installed successfully!"
echo "======================================================================"
echo ""
echo "📊 Current crontab:"
echo "----------------------------------------------------------------------"
crontab -l | grep "local_hourly_task.py" || echo "(No entries found)"
echo "----------------------------------------------------------------------"
echo ""
echo "📝 Next steps:"
echo "  1. The task will run automatically every hour at minute 0"
echo "  2. Check logs: tail -f $LOG_FILE"
echo "  3. Test manually: source $ENV_FILE && python3 \"$SCRIPT_PATH\""
echo "  4. Remove cronjob: crontab -e (then delete the line)"
echo ""
echo "⏰ Next scheduled run: $(date -v +1H '+%Y-%m-%d %H:00:00')"
echo ""
echo "======================================================================"
