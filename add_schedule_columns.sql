-- Add trigger_config and schedule_config columns to schedule_tasks table
ALTER TABLE schedule_tasks
ADD COLUMN IF NOT EXISTS trigger_config JSONB DEFAULT '{}',
ADD COLUMN IF NOT EXISTS schedule_config JSONB DEFAULT '{}';

-- Verify columns were added
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'schedule_tasks'
  AND column_name IN ('trigger_config', 'schedule_config');
