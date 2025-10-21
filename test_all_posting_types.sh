#!/bin/bash

echo "📊 Performance Test - All Posting Types"
echo "========================================"
echo ""

# Test configuration
STOCK_CODE="2330"
STOCK_NAME="台積電"
KOL_SERIAL=208

# Results array
declare -A results

# Function to test a posting type
test_posting_type() {
    local posting_type=$1
    local kol_persona=$2
    local max_words=$3
    local test_name=$4

    echo "Testing: $test_name"
    echo "  Type: $posting_type"
    echo "  Persona: $kol_persona"
    echo "  Max words: $max_words"
    echo ""

    # Start timer
    START=$(python3 -c "import time; print(time.time())")

    # Make API call
    SESSION_ID=$(date +%s)000
    RESPONSE=$(curl -s -X POST "https://forumautoposter-production.up.railway.app/api/manual-posting" \
      -H "Content-Type: application/json" \
      -d "{
        \"stock_code\": \"$STOCK_CODE\",
        \"stock_name\": \"$STOCK_NAME\",
        \"kol_serial\": $KOL_SERIAL,
        \"kol_persona\": \"$kol_persona\",
        \"session_id\": $SESSION_ID,
        \"trigger_type\": \"perf_test_$posting_type\",
        \"posting_type\": \"$posting_type\",
        \"max_words\": $max_words
      }" 2>&1)

    # End timer
    END=$(python3 -c "import time; print(time.time())")
    DURATION=$(python3 -c "print(f'{$END - $START:.2f}')")

    # Parse response
    SUCCESS=$(echo "$RESPONSE" | python3 -c "import sys, json; d=json.load(sys.stdin) if sys.stdin.read() else {}; print('yes' if d.get('success') else 'no')" 2>/dev/null || echo "no")

    if [ "$SUCCESS" = "yes" ]; then
        POST_ID=$(echo "$RESPONSE" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('post_id', 'N/A'))" 2>/dev/null)
        echo "  ✅ Success! Duration: ${DURATION}s"
        echo "  Post ID: $POST_ID"
        results["$posting_type"]=$DURATION
    else
        echo "  ❌ Failed! Duration: ${DURATION}s"
        echo "  Response: $(echo "$RESPONSE" | head -c 200)"
        results["$posting_type"]="FAILED"
    fi

    echo ""
}

# Test 1: Interaction (short, question-based)
test_posting_type "interaction" "technical" 100 "TEST 1: Interaction (互動發問)"

echo "Waiting 3 seconds..."
sleep 3
echo ""

# Test 2: Analysis (medium, analytical)
test_posting_type "analysis" "fundamental" 200 "TEST 2: Analysis (分析型)"

echo "Waiting 3 seconds..."
sleep 3
echo ""

# Test 3: Personalized (long, personalized)
test_posting_type "personalized" "mixed" 250 "TEST 3: Personalized (個人化)"

echo ""
echo "=========================================="
echo "📊 Performance Summary"
echo "=========================================="
echo ""

# Calculate statistics
echo "| Posting Type | Duration | Status |"
echo "|--------------|----------|--------|"

for type in interaction analysis personalized; do
    duration=${results[$type]}
    if [ "$duration" = "FAILED" ]; then
        echo "| $type | FAILED | ❌ |"
    else
        echo "| $type | ${duration}s | ✅ |"
    fi
done

echo ""

# Calculate average (excluding failures)
TOTAL=0
COUNT=0
for type in interaction analysis personalized; do
    duration=${results[$type]}
    if [ "$duration" != "FAILED" ]; then
        TOTAL=$(python3 -c "print($TOTAL + $duration)")
        COUNT=$((COUNT + 1))
    fi
done

if [ $COUNT -gt 0 ]; then
    AVERAGE=$(python3 -c "print(f'{$TOTAL / $COUNT:.2f}')")
    echo "Average Duration: ${AVERAGE}s"
    echo ""

    # Projections
    echo "Batch Projections:"
    echo "  10 posts: $(python3 -c "print(f'{$AVERAGE * 10 / 60:.1f}')") minutes"
    echo "  50 posts: $(python3 -c "print(f'{$AVERAGE * 50 / 60:.1f}')") minutes"
    echo "  100 posts: $(python3 -c "print(f'{$AVERAGE * 100 / 60:.1f}')") minutes"
fi

echo ""
echo "✅ Performance test complete!"
echo ""
