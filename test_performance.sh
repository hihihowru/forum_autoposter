#!/bin/bash

echo "🚀 Forum AutoPoster - Performance Test"
echo "======================================="
echo ""

# Wait for deployment if needed
echo "Checking if endpoint is available..."
HEALTH=$(curl -s "https://forumautoposter-production.up.railway.app/health" 2>/dev/null)
echo "$HEALTH" | python3 -c "import sys, json; d=json.load(sys.stdin); ts=d.get('timestamp', '')[:19]; print(f'Current deployment: {ts}')" 2>/dev/null

echo ""
echo "Running performance test..."
echo "Test parameters:"
echo "  Stock: 2330 (台積電)"
echo "  KOL: 208"
echo "  Type: interaction"
echo "  Max words: 150"
echo ""

# Run performance test
RESULT=$(curl -s -X POST "https://forumautoposter-production.up.railway.app/api/debug/performance-test" \
  -H "Content-Type: application/json" \
  -d '{
    "stock_code": "2330",
    "stock_name": "台積電",
    "kol_serial": 208,
    "kol_persona": "technical",
    "posting_type": "interaction",
    "max_words": 150
  }' 2>/dev/null)

# Check if result is valid JSON
if echo "$RESULT" | python3 -c "import sys, json; json.load(sys.stdin)" 2>/dev/null; then
  echo "$RESULT" | python3 -c "
import sys, json

d = json.load(sys.stdin)

if d.get('success'):
    print('✅ Performance Test Complete!')
    print('=' * 70)
    print()

    # Summary
    summary = d.get('summary', {})
    print(f'⏱️  Total Time: {summary.get(\"total_time_seconds\")} seconds ({summary.get(\"total_time_ms\")} ms)')
    print(f'🔴 Slowest Step: {summary.get(\"slowest_step\")} ({summary.get(\"slowest_time_ms\")} ms)')
    print(f'🤖 Model Used: {d.get(\"model_used\")}')
    print(f'📝 Post ID: {d.get(\"post_id\")}')
    print()

    # Detailed breakdown
    print('📊 Time Breakdown:')
    print('=' * 70)

    breakdown = d.get('breakdown', {})
    for step_key in ['1_parse_request', '2_model_selection_db', '3_gpt_generation', '4_alternative_versions', '5_database_write']:
        step = breakdown.get(step_key, {})
        time_ms = step.get('time_ms', 0)
        pct = step.get('percentage', 0)
        desc = step.get('description', '')

        # Create visual bar
        bar_length = int(pct / 2)  # Scale to 50 chars max
        bar = '█' * bar_length

        print(f'{step_key}: {desc}')
        print(f'  Time: {time_ms:>8.2f} ms  |  {pct:>5.1f}%  {bar}')
        print()

    print('=' * 70)
    print()

    # Performance analysis
    timings = d.get('timings_ms', {})
    gpt_time = timings.get('3_gpt_generation', 0)
    alt_time = timings.get('4_alternative_versions', 0)
    db_time = timings.get('5_database_write', 0)
    total_time = timings.get('total_time', 0)

    print('💡 Performance Analysis:')
    print('-' * 70)

    if gpt_time > 2000:
        print('⚠️  GPT generation is slow (>2s) - OpenAI API latency')
    if alt_time > 1000:
        print('⚠️  Alternative versions generation is slow (>1s)')
    if db_time > 200:
        print('⚠️  Database write is slow (>200ms)')
    if total_time < 3000:
        print('✅ Good overall performance (<3s total)')
    elif total_time < 5000:
        print('⚠️  Moderate performance (3-5s total)')
    else:
        print('🔴 Slow performance (>5s total) - needs optimization')

    print()

else:
    print('❌ Performance Test Failed')
    print(f'Error: {d.get(\"error\", \"Unknown error\")}')
"
else
  echo "❌ Failed to get valid response from performance test endpoint"
  echo "Response:"
  echo "$RESULT"
  echo ""
  echo "Possible reasons:"
  echo "1. Endpoint not deployed yet (check Railway build status)"
  echo "2. Server error"
  echo "3. Network issue"
fi
