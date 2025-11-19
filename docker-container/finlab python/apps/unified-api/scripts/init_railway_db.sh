#!/bin/bash
# Railway PostgreSQL Database Initialization Script
# Run this to set up all required tables and schema

set -e

echo "🗄️  Initializing Railway PostgreSQL Database..."

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo "❌ ERROR: DATABASE_URL environment variable is not set!"
    echo "Please set it to your Railway PostgreSQL connection string:"
    echo "export DATABASE_URL='postgresql://postgres:password@host:port/dbname'"
    exit 1
fi

echo "✅ DATABASE_URL is set"
echo "📊 Applying migrations..."

# Change to migrations directory
cd "$(dirname "$0")/../migrations"

# Apply migrations in order
MIGRATIONS=(
    "add_reaction_bot_tables.sql"
    "create_hourly_reaction_stats.sql"
    "create_reaction_logs.sql"
    "add_engagement_system.sql"
    "add_prompt_templates.sql"
    "add_trending_topics_support.sql"
)

for migration in "${MIGRATIONS[@]}"; do
    if [ -f "$migration" ]; then
        echo "  📄 Applying: $migration"
        psql "$DATABASE_URL" -f "$migration"
        echo "  ✅ Applied: $migration"
    else
        echo "  ⚠️  Skipping (not found): $migration"
    fi
done

echo ""
echo "✅ Database initialization complete!"
echo "🎉 All migrations have been applied successfully"
