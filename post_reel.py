"""
Sorumluluk: Hazırlanmış reel videoyu Instagram hesabına yükler.
- Kullanır: instagrapi
- DRY_RUN=1 ise upload atlanır (test için)
- Kimlik bilgileri çevre değişkenleri: IG_USERNAME, IG_PASSWORD
"""

import json
import os
from typing import Optional


USERNAME = os.environ.get("IG_USERNAME") or os.environ.get("USERNAME")
PASSWORD = os.environ.get("IG_PASSWORD") or os.environ.get("PASSWORD")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SESSION_PATH = os.path.join(BASE_DIR, "instagrapi_settings.json")


def _ensure_file_dir(path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)


def upload_reel(video_path: str, caption: Optional[str] = None) -> None:
    # Dry run: yükleme yerine sadece bilgilendirme
    if os.environ.get("DRY_RUN") == "1":
        print(f"[DRY_RUN] Reeli atlayarak devam ediyorum. Video: {video_path}\nCaption:\n{caption}")
        return

    if not USERNAME or not PASSWORD:
        raise ValueError("IG_USERNAME ve IG_PASSWORD çevre değişkenlerini tanımlayın.")

    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video dosyası bulunamadı: {video_path}")

    # instagrapi import'unu fonksiyon içinde yaparak bağımlılığı erteliyoruz
    from instagrapi import Client

    cl = Client()

    # Varsa önceki oturum ayarlarını yükle
    if os.path.exists(SESSION_PATH):
        try:
            with open(SESSION_PATH, "r", encoding="utf-8") as f:
                settings = json.load(f)
            cl.set_settings(settings)
        except Exception:
            pass

    # Giriş
    cl.login(USERNAME, PASSWORD)

    # Başarılı girişten sonra güncel oturum ayarlarını kaydet
    try:
        _ensure_file_dir(SESSION_PATH)
        with open(SESSION_PATH, "w", encoding="utf-8") as f:
            json.dump(cl.get_settings(), f)
    except Exception:
        pass

    try:
        media = cl.clip_upload(video_path, caption=caption)
        print("Reel yüklendi. media id:", getattr(media, "pk", None))
    except Exception as e:
        print("Reel upload failed:", e)
        raise
    finally:
        try:
            cl.logout()
        except Exception:
            pass


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python post_reel.py /path/to/video.mp4 'Caption text'")
        raise SystemExit(1)

    video = sys.argv[1]
    caption = sys.argv[2] if len(sys.argv) > 2 else None
    upload_reel(video, caption)