"""
Automated weekly report scheduler.
Run: python scheduler.py
Sends report every Monday at 8:00 AM.
"""
import schedule
import time
from datetime import datetime
from main import run_pipeline


def weekly_job():
    print(f"\n⏰ Scheduled run triggered at {datetime.now()}")
    run_pipeline(use_demo=False, send_email=True, days=365)


def main():
    print("🕐 Scheduler started. Reports run every Monday at 08:00.")
    print("   Press Ctrl+C to stop.\n")

    schedule.every().monday.at("08:00").do(weekly_job)

    # Also run immediately on start for testing
    # weekly_job()

    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    main()
