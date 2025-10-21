#!/bin/bash

# Test script to verify connection pooling deployment fixes

API_BASE="https://forumautoposter-production.up.railway.app"

echo "=========================================="
echo "Testing Deployment Fixes"
echo "=========================================="
echo ""

# Test 1: Health check
echo "1️⃣  Testing /health endpoint..."
HEALTH=$(curl -s "$API_BASE/health")
echo "$HEALTH" | python3 -m json.tool
echo ""

# Test 2: Posts endpoint (should return posts, not error)
echo "2️⃣  Testing /api/posts endpoint..."
POSTS=$(curl -s "$API_BASE/api/posts?skip=0&limit=2")
echo "$POSTS" | python3 -m json.tool
echo ""

# Check if posts endpoint succeeded
SUCCESS=$(echo "$POSTS" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('success', False))")
COUNT=$(echo "$POSTS" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('count', 0))")
echo "✅ Posts API Success: $SUCCESS, Count: $COUNT"
echo ""

# Test 3: Schedule status endpoint (should be fast, not 20+ seconds)
echo "3️⃣  Testing /api/schedule/scheduler/status endpoint..."
START=$(date +%s)
STATUS=$(curl -s "$API_BASE/api/schedule/scheduler/status")
END=$(date +%s)
DURATION=$((END - START))
echo "$STATUS" | python3 -m json.tool
echo "⏱️  Response time: ${DURATION}s (should be < 2s)"
echo ""

# Test 4: Concurrent requests (test connection pooling)
echo "4️⃣  Testing concurrent requests (connection pooling)..."
START=$(date +%s)
curl -s "$API_BASE/api/posts?limit=1" > /dev/null &
curl -s "$API_BASE/api/posts?limit=1" > /dev/null &
curl -s "$API_BASE/api/posts?limit=1" > /dev/null &
wait
END=$(date +%s)
DURATION=$((END - START))
echo "✅ 3 concurrent requests completed in ${DURATION}s"
echo ""

# Test 5: KOL list endpoint
echo "5️⃣  Testing /api/kol/list endpoint..."
KOLS=$(curl -s "$API_BASE/api/kol/list" | python3 -c "import sys, json; data=json.load(sys.stdin); print(f'KOL count: {len(data) if isinstance(data, list) else 0}')")
echo "$KOLS"
echo ""

echo "=========================================="
echo "Test Summary"
echo "=========================================="
if [ "$SUCCESS" = "True" ] && [ "$COUNT" -gt 0 ]; then
    echo "✅ Posts API: FIXED - returning $COUNT posts"
else
    echo "❌ Posts API: FAILED - still returning 0 posts or error"
fi

if [ "$DURATION" -lt 5 ]; then
    echo "✅ Schedule Status: FIXED - response time ${DURATION}s"
else
    echo "❌ Schedule Status: SLOW - response time ${DURATION}s"
fi

echo ""
echo "Done!"
