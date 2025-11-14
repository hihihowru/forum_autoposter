-- Migration: Add trending topics support to post_records table
-- Created: 2025-01-14
-- Description: Add columns to track trending topics in posts

-- Add trending topic columns to post_records table
ALTER TABLE post_records
ADD COLUMN IF NOT EXISTS has_trending_topic BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS topic_content TEXT;

-- Create index for faster topic queries
CREATE INDEX IF NOT EXISTS idx_post_records_has_trending_topic ON post_records(has_trending_topic);
CREATE INDEX IF NOT EXISTS idx_post_records_topic_id ON post_records(topic_id);

-- Add comment to columns
COMMENT ON COLUMN post_records.has_trending_topic IS 'Whether this post is generated from a trending topic';
COMMENT ON COLUMN post_records.topic_id IS 'ID of the trending topic from CMoney API (if applicable)';
COMMENT ON COLUMN post_records.topic_title IS 'Title of the trending topic (if applicable)';
COMMENT ON COLUMN post_records.topic_content IS 'Content/description of the trending topic (if applicable)';

-- Update existing posts to have default values
UPDATE post_records
SET has_trending_topic = FALSE
WHERE has_trending_topic IS NULL;
