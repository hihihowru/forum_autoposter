-- Cancel all active schedules
-- Run this before testing the scheduler

-- Show current active schedules
SELECT
    schedule_id,
    schedule_name,
    status,
    created_at,
    daily_execution_time
FROM schedule_tasks
WHERE status = 'active'
ORDER BY created_at DESC;

-- Count active schedules
SELECT COUNT(*) as active_count FROM schedule_tasks WHERE status = 'active';

-- Update all active schedules to cancelled
UPDATE schedule_tasks
SET
    status = 'cancelled',
    updated_at = NOW()
WHERE status = 'active';

-- Verify cancellation
SELECT COUNT(*) as active_count FROM schedule_tasks WHERE status = 'active';
SELECT COUNT(*) as cancelled_count FROM schedule_tasks WHERE status = 'cancelled';

-- Show summary of all schedules by status
SELECT
    status,
    COUNT(*) as count
FROM schedule_tasks
GROUP BY status
ORDER BY count DESC;
