"""
Quick script to query the database for debugging
"""
import psycopg2
import json
import os

# Get database URL from environment or use Railway variable
DATABASE_URL = os.getenv("DATABASE_URL") or os.getenv("DATABASE_PRIVATE_URL")

if not DATABASE_URL:
    print("❌ No DATABASE_URL found in environment")
    exit(1)

try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    # Query for the latest posts with those session IDs
    query = """
        SELECT id, session_id, generation_params
        FROM generated_posts
        WHERE session_id IN ('1761061609389', '1761060872395')
        ORDER BY id DESC
        LIMIT 5;
    """

    cursor.execute(query)
    results = cursor.fetchall()

    print(f"📊 Found {len(results)} posts\n")

    for row in results:
        post_id, session_id, generation_params = row
        print(f"{'='*80}")
        print(f"Post ID: {post_id}")
        print(f"Session ID: {session_id}")
        print(f"Generation Params Type: {type(generation_params)}")

        if generation_params:
            if isinstance(generation_params, str):
                try:
                    params = json.loads(generation_params)
                    print(f"✅ Parsed as JSON")
                    print(f"Has full_triggers_config: {'full_triggers_config' in params}")
                    if 'full_triggers_config' in params:
                        print(f"full_triggers_config value: {json.dumps(params['full_triggers_config'], ensure_ascii=False, indent=2)}")
                    else:
                        print(f"Keys in generation_params: {list(params.keys())}")
                        print(f"Full generation_params:\n{json.dumps(params, ensure_ascii=False, indent=2)}")
                except Exception as e:
                    print(f"❌ Failed to parse: {e}")
                    print(f"Raw value (first 500 chars): {generation_params[:500]}")
            else:
                print(f"generation_params is not a string: {generation_params}")
        else:
            print("⚠️ generation_params is NULL")
        print()

    cursor.close()
    conn.close()

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
