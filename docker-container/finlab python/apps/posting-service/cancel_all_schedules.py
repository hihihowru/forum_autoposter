"""
Script to cancel all active schedules
Run this before testing the scheduler to avoid executing old schedules
"""

import asyncio
import sys
from schedule_database import schedule_db_service

async def cancel_all_active_schedules():
    """Cancel all active schedules in the database"""

    print("🔍 Fetching all active schedules...")

    # Get all active schedules
    active_schedules = await schedule_db_service.get_active_schedule_tasks()

    print(f"📊 Found {len(active_schedules)} active schedules")

    if len(active_schedules) == 0:
        print("✅ No active schedules to cancel")
        return

    print("\n📋 Active schedules:")
    for idx, schedule in enumerate(active_schedules, 1):
        schedule_id = schedule['schedule_id']
        schedule_name = schedule.get('schedule_name', 'Unknown')
        created_at = schedule.get('created_at', 'Unknown')
        print(f"   {idx}. {schedule_id[:8]}... - {schedule_name} (Created: {created_at})")

    print(f"\n⚠️  Cancelling all {len(active_schedules)} active schedules...")

    success_count = 0
    failure_count = 0

    for schedule in active_schedules:
        schedule_id = schedule['schedule_id']
        schedule_name = schedule.get('schedule_name', 'Unknown')

        try:
            # Cancel the schedule
            success = await schedule_db_service.cancel_schedule_task(schedule_id)

            if success:
                print(f"   ✅ Cancelled: {schedule_id[:8]}... - {schedule_name}")
                success_count += 1
            else:
                print(f"   ❌ Failed to cancel: {schedule_id[:8]}... - {schedule_name}")
                failure_count += 1

        except Exception as e:
            print(f"   ❌ Error cancelling {schedule_id[:8]}...: {e}")
            failure_count += 1

    print("\n📊 Summary:")
    print(f"   ✅ Successfully cancelled: {success_count}")
    print(f"   ❌ Failed to cancel: {failure_count}")
    print(f"   📈 Total processed: {len(active_schedules)}")

    if success_count == len(active_schedules):
        print("\n🎉 All active schedules successfully cancelled!")
        return 0
    else:
        print("\n⚠️  Some schedules failed to cancel")
        return 1

async def verify_cancellation():
    """Verify that all schedules are now cancelled"""
    print("\n🔍 Verifying cancellation...")

    active_schedules = await schedule_db_service.get_active_schedule_tasks()

    if len(active_schedules) == 0:
        print("✅ Verification successful: No active schedules remaining")
        return True
    else:
        print(f"⚠️  Verification failed: {len(active_schedules)} schedules still active")
        return False

async def main():
    """Main function"""
    print("=" * 60)
    print("Cancel All Active Schedules")
    print("=" * 60)
    print()

    try:
        # Cancel all schedules
        exit_code = await cancel_all_active_schedules()

        # Verify cancellation
        verified = await verify_cancellation()

        if verified and exit_code == 0:
            print("\n✅ All done! Safe to test the scheduler now.")
            sys.exit(0)
        else:
            print("\n⚠️  Please check the errors above")
            sys.exit(1)

    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
