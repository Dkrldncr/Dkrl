from apscheduler.schedulers.blocking import BlockingScheduler
import subprocess
import datetime
import os


PYTHON_BIN = os.environ.get("PYTHON_BIN", "python3")


def run_main_once():
    print("[JOB BAŞLADI]", datetime.datetime.now())
    try:
        subprocess.run([PYTHON_BIN, "main.py"], check=False)
    finally:
        print("[JOB BİTTİ]", datetime.datetime.now())


def run_fetch():
    print("[FETCH BAŞLADI]", datetime.datetime.now())
    try:
        subprocess.run([PYTHON_BIN, "fetch_questions.py"], check=False)
    finally:
        print("[FETCH BİTTİ]", datetime.datetime.now())


if __name__ == "__main__":
    scheduler = BlockingScheduler()

    # Soruları günde 1 kez güncelle (gece 03:00)
    scheduler.add_job(run_fetch, "cron", hour=3, minute=0)

    # Paylaşım saatleri
    for h in [8, 11, 13, 18, 22]:
        scheduler.add_job(run_main_once, "cron", hour=h, minute=0)

    print("Scheduler başlatıldı...")
    scheduler.start()