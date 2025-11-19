# Railway PostgreSQL Setup Guide

## Problem
The Railway deployment is failing because the PostgreSQL database service is not properly configured or initialized.

## Solution

### Step 1: Add PostgreSQL Service to Railway

1. Go to your Railway project dashboard
2. Click **"+ New"** → **"Database"** → **"Add PostgreSQL"**
3. Railway will automatically provision a PostgreSQL instance and create a `DATABASE_URL` variable

### Step 2: Verify Environment Variable

Make sure your main app service has access to the `DATABASE_URL`:
1. Go to your app service in Railway
2. Click **"Variables"** tab
3. Confirm `DATABASE_URL` is listed (it should be automatically linked from the PostgreSQL service)
4. The format should be: `postgresql://postgres:***@***.****.railway.app:****/*****`

### Step 3: Initialize Database Schema

You have TWO options to run the migrations:

#### Option A: Using Railway CLI (Recommended)

```bash
# Install Railway CLI if you haven't
npm install -g @railway/cli

# Login to Railway
railway login

# Link to your project
railway link

# Connect to PostgreSQL and run migrations
cd "docker-container/finlab python/apps/unified-api/scripts"
railway run ./init_railway_db.sh
```

#### Option B: Manual SQL Execution via Railway Dashboard

1. In Railway dashboard, click on your **PostgreSQL** service
2. Go to **"Data"** tab → **"Query"**
3. Copy and paste each migration file content in this order:
   - `migrations/add_reaction_bot_tables.sql`
   - `migrations/create_hourly_reaction_stats.sql`
   - `migrations/create_reaction_logs.sql`
   - `migrations/add_engagement_system.sql`
   - `migrations/add_prompt_templates.sql`
   - `migrations/add_trending_topics_support.sql`
4. Click **"Run"** for each migration

#### Option C: Using psql locally

```bash
# Export your DATABASE_URL from Railway
export DATABASE_URL="postgresql://postgres:password@containers-us-west-**.railway.app:****/*****"

# Run the initialization script
cd "docker-container/finlab python/apps/unified-api/scripts"
./init_railway_db.sh
```

### Step 4: Redeploy Your Application

After the database is initialized:
1. Go to your app service in Railway
2. Click **"Deployments"** tab
3. Click **"Redeploy"** on the latest deployment

The app should now start successfully and connect to the PostgreSQL database!

## Verification

After deployment, check the logs to ensure:
- ✅ No `ModuleNotFoundError: No module named 'services'` (fixed in Dockerfile)
- ✅ No database connection errors
- ✅ App starts and shows "✓ Database connection successful"

## Troubleshooting

### If you still see errors:

1. **Check PostgreSQL service is running:**
   - Go to PostgreSQL service in Railway
   - Verify status is "Active"

2. **Check DATABASE_URL is correct:**
   - In app service → Variables tab
   - DATABASE_URL should start with `postgresql://`

3. **Check for connection errors in logs:**
   - Look for messages like "could not connect to server"
   - Verify PostgreSQL service is in the same project

4. **Verify tables were created:**
   - In PostgreSQL service → Data tab
   - Run: `SELECT tablename FROM pg_tables WHERE schemaname='public';`
   - Should see tables like `reaction_bot_config`, `reaction_bot_logs`, etc.
