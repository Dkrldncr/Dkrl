"""
Sorumluluk: Hazırlanmış reel videoyu Instagram hesabına yükler.
- Kullanır: instagrapi
- Not: Reels API ve sticker özellikleri sürüme göre değişebilir.
"""

from instagrapi import Client
import os

USERNAME = os.environ.get("IG_USERNAME", "your_username")
PASSWORD = os.environ.get("IG_PASSWORD", "your_password")


def upload_reel(video_path: str, caption: str | None = None) -> None:
    cl = Client()
    cl.login(USERNAME, PASSWORD)
    try:
        media = cl.clip_upload(video_path, caption=caption)
        print("Reel uploaded. media id:", getattr(media, "pk", None))
    except Exception as e:
        print("Reel upload failed:", e)
    finally:
        try:
            cl.logout()
        except Exception:
            pass


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print('Usage: python post_reel.py /path/to/video.mp4 "Caption text"')
        raise SystemExit(1)

    video = sys.argv[1]
    caption = sys.argv[2] if len(sys.argv) > 2 else None
    upload_reel(video, caption)