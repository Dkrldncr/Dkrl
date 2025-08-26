"""
APScheduler ile zamanlayıcı:
- Soruları günde 1 kez (03:00) günceller
- 08:00, 11:00, 13:00, 18:00, 22:00'de paylaşım yapar
"""

import datetime
import os
import signal
import sys

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone

from fetch_questions import fetch_and_store_all
from main import run_once


TZ = timezone(os.environ.get("TZ", "Europe/Istanbul"))


def fetch_job() -> None:
    print("[FETCH JOB BAŞLADI]", datetime.datetime.now(TZ))
    try:
        fetch_and_store_all()
    except Exception as exc:
        print("[FETCH JOB HATA]", exc)
    print("[FETCH JOB BİTTİ]", datetime.datetime.now(TZ))


def post_job() -> None:
    print("[POST JOB BAŞLADI]", datetime.datetime.now(TZ))
    try:
        run_once()
    except Exception as exc:
        print("[POST JOB HATA]", exc)
    print("[POST JOB BİTTİ]", datetime.datetime.now(TZ))


scheduler = BlockingScheduler(timezone=TZ)

# Soruları günde 1 kez güncelle (gece 03:00)
scheduler.add_job(fetch_job, CronTrigger(hour=3, minute=0))

# Paylaşım saatleri
for h in [8, 11, 13, 18, 22]:
    scheduler.add_job(post_job, CronTrigger(hour=h, minute=0))

print("Scheduler başlatıldı... (TZ: Europe/Istanbul)")


def _graceful_shutdown(signum, frame):
    print(f"Sinyal alındı ({signum}), scheduler durduruluyor...")
    scheduler.shutdown(wait=False)
    sys.exit(0)


signal.signal(signal.SIGINT, _graceful_shutdown)
signal.signal(signal.SIGTERM, _graceful_shutdown)

scheduler.start()