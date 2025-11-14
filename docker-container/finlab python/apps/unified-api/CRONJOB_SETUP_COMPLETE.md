# CMoney Hourly Reaction Bot - Cronjob Setup Complete

## Summary

The hourly reaction bot is now set up to run automatically on your local Mac every hour!

## What Was Fixed

### 1. Reaction API Fixed
- **Changed method**: POST → PUT
- **Changed URL**: `/api/Interactive/Reaction/{articleId}` → `/api/Article/{articleId}/Emoji/{emojiType}`
- **Added headers**: `X-Version: 2.0` + proper trace context
- **File**: `cmoney_client.py:745-799`

### 2. Database Schema Fixed
- Fixed column names: `username` → `nickname`
- Fixed status check: `is_active = true` → `status = 'active'`
- **File**: `hourly_reaction_service.py:64-78`

### 3. Service Return Values Fixed
- Added return stats from `run_hourly_task()`
- Added support for passing `article_ids` parameter
- **File**: `hourly_reaction_service.py:218-303`

### 4. Local Task Script Updated
- Properly passes article_ids to service
- Handles empty article lists
- **File**: `local_hourly_task.py:81-101`

## Cronjob Configuration

**Schedule**: Every hour at minute 0
**Command**:
```bash
0 * * * * source /Users/willchen/.hourly_task_env && cd "/Users/willchen/Documents/autoposter/forum_autoposter/docker-container/finlab python/apps/unified-api" && /Users/willchen/anaconda3/bin/python3 "/Users/willchen/Documents/autoposter/forum_autoposter/docker-container/finlab python/apps/unified-api/local_hourly_task.py" >> "/Users/willchen/Library/Logs/cmoney_hourly_task.log" 2>&1
```

**Log file**: `/Users/willchen/Library/Logs/cmoney_hourly_task.log`

## Workflow

Every hour, the cronjob will:

1. **Fetch articles** from Kafka (`anya.cmoney.tw`) for the past hour
2. **Load KOL pool** from Railway PostgreSQL database
3. **Rotate through KOLs** to like articles:
   - Each KOL likes 10 articles before switching
   - 2-second delay between reactions to avoid rate limiting
4. **Save statistics** to Railway database:
   - Article IDs processed
   - Like success rate
   - KOL pool used
   - Timestamps

## How to Monitor

### Check if cronjob is running:
```bash
crontab -l
```

### Watch logs in real-time:
```bash
tail -f /Users/willchen/Library/Logs/cmoney_hourly_task.log
```

### Check database stats:
```bash
cd "/Users/willchen/Documents/autoposter/forum_autoposter/docker-container/finlab python/apps/unified-api"
python3 check_saved_articles.py
```

### Run manually for testing:
```bash
source ~/.hourly_task_env
cd "/Users/willchen/Documents/autoposter/forum_autoposter/docker-container/finlab python/apps/unified-api"
python3 local_hourly_task.py
```

## Verified Working

✅ **Reaction API**: Tested with article 174900272, successfully liked
✅ **Article fetching**: Tested, fetched 581 articles from Kafka
✅ **Database connection**: Tested, successfully loaded 28 KOLs
✅ **Cronjob**: Installed and scheduled

## Next Scheduled Run

The task will run at the top of every hour:
- 18:00
- 19:00
- 20:00
- etc.

## How to Remove Cronjob

If you need to stop the hourly task:

```bash
crontab -e
# Delete the line containing "local_hourly_task.py"
# Save and exit
```

Or remove all cronjobs:
```bash
crontab -r
```

## Database Details

- **Host**: yamabiko.proxy.rlwy.net:17910
- **Database**: railway
- **Table**: hourly_reaction_stats
- **KOL Table**: kol_profiles (28 active KOLs)

## Files Created/Modified

1. `cmoney_client.py` - Fixed reaction API
2. `hourly_reaction_service.py` - Fixed schema & return values
3. `local_hourly_task.py` - Updated to pass article_ids
4. `setup_cronjob.sh` - Automated cronjob installer
5. `~/.hourly_task_env` - Environment variables
6. `CRONJOB_SETUP_COMPLETE.md` - This file

## Architecture

```
Local Mac (with VPN)
├── Cronjob (every hour)
│   └── local_hourly_task.py
│       ├── Fetch articles from anya.cmoney.tw (Kafka)
│       ├── Load KOL credentials from Railway DB
│       ├── Like articles via forumservice.cmoney.tw
│       └── Save stats to Railway DB
│
└── Railway PostgreSQL (public access)
    ├── kol_profiles table (28 KOLs)
    └── hourly_reaction_stats table (statistics)
```

## Success!

Everything is ready! The bot will automatically run every hour and like CMoney forum articles using your KOL pool. Check the logs after the next hour to verify it's working as expected.
