-- Delete all schedules from schedule_tasks table
-- Backup已創建: schedule_backup_20251021_153036.json

BEGIN;

-- Show count before deletion
SELECT COUNT(*) as total_schedules_before_delete FROM schedule_tasks;

-- Delete all schedules
DELETE FROM schedule_tasks;

-- Show count after deletion
SELECT COUNT(*) as total_schedules_after_delete FROM schedule_tasks;

COMMIT;

-- Confirm deletion
SELECT 'All schedules deleted successfully!' as status;
