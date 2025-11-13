#!/bin/bash

# Hourly Reaction API 測試腳本
# 用法：./test_hourly_api.sh [BASE_URL]

BASE_URL="${1:-https://forum-autoposter-backend-production.up.railway.app}"

echo "🧪 Testing Hourly Reaction API Endpoints"
echo "Base URL: $BASE_URL"
echo "=========================================="

# Test 1: Health Check
echo -e "\n1️⃣  Health Check"
curl -s "${BASE_URL}/api/reaction-bot/health" | jq '.'

# Test 2: Fetch Articles (check if data is available)
echo -e "\n2️⃣  Fetch Articles (past 1 hour)"
curl -s "${BASE_URL}/api/reaction-bot/fetch-articles?hours_back=1" | jq '.'

# Test 3: Check if hourly_reaction_stats table has data
echo -e "\n3️⃣  Check Hourly Stats (latest)"
curl -s "${BASE_URL}/api/reaction-bot/hourly-stats/latest" | jq '.'

# Test 4: Get summary
echo -e "\n4️⃣  Get Hourly Stats Summary (past 24h)"
curl -s "${BASE_URL}/api/reaction-bot/hourly-stats/summary?hours=24" | jq '.'

# Test 5: List stats
echo -e "\n5️⃣  List Hourly Stats (first 5)"
curl -s "${BASE_URL}/api/reaction-bot/hourly-stats?limit=5&offset=0" | jq '.'

echo -e "\n=========================================="
echo "✅ Testing complete!"
echo ""
echo "💡 To manually run hourly task:"
echo "   curl -X POST \"${BASE_URL}/api/reaction-bot/hourly-task/run\""
echo ""
echo "⚠️  Note: The hourly task may take 5-10 minutes to complete"
echo "   depending on the number of articles and KOLs"
