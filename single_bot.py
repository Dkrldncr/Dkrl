"""
Tek Dosya: Trafik Test Botu (Reels + Story Quiz/Poll + Scheduler)

Kullanım:
  # Bağımlılıklar (FFmpeg gerekli)
  pip install -r requirements.txt
  sudo apt-get update && sudo apt-get install -y ffmpeg  # Linux

  # Test için veritabanını seed etmek (opsiyonel)
  python single_bot.py seed

  # Tek seferlik akış (fetch -> reel -> used -> story)
  export IG_USERNAME=... IG_PASSWORD=... TZ=Europe/Istanbul
  # Deneme için yükleme atlamak isterseniz: DRY_RUN=1
  python single_bot.py run-once

  # Zamanlayıcı (03:00 fetch, 08/11/13/18/22 post)
  python single_bot.py scheduler
"""

import argparse
import hashlib
import json
import os
import signal
import sqlite3
import sys
import textwrap
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageClip

# APScheduler ve TZ
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone

# ------------------- Genel Ayarlar -------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "questions.db")
OUTPUT_DIR = os.path.join(BASE_DIR, "output_reels")
IMG_SIZE = (1080, 1920)

FONT_PATH = os.environ.get("FONT_PATH")  # opsiyonel özel font
TZ = timezone(os.environ.get("TZ", "Europe/Istanbul"))
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/118.0 Safari/537.36"
)
DEFAULT_HEADERS = {"User-Agent": USER_AGENT}
REQUEST_TIMEOUT_SECONDS = 20

USERNAME = os.environ.get("IG_USERNAME") or os.environ.get("USERNAME")
PASSWORD = os.environ.get("IG_PASSWORD") or os.environ.get("PASSWORD")
SESSION_PATH = os.path.join(BASE_DIR, "instagrapi_settings.json")

# ------------------- DB Helpers -------------------

def init_db(db_path: str = DB_PATH) -> None:
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY,
            uid TEXT UNIQUE,
            question TEXT,
            option_a TEXT,
            option_b TEXT,
            option_c TEXT,
            option_d TEXT,
            correct TEXT,
            source TEXT,
            fetched_at INTEGER,
            used INTEGER DEFAULT 0
        )
        """
    )
    conn.commit()
    conn.close()


def question_uid(question_text: str, options: List[Optional[str]]) -> str:
    normalized = question_text.strip() + "||" + "||".join([o.strip() for o in options if o])
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def insert_question(db_path: str, q: Dict) -> bool:
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    try:
        uid = question_uid(
            q.get("question", ""),
            [
                q.get("option_a", ""),
                q.get("option_b", ""),
                q.get("option_c", ""),
                q.get("option_d", ""),
            ],
        )
        c.execute(
            """
            INSERT INTO questions (
                uid, question, option_a, option_b, option_c, option_d,
                correct, source, fetched_at, used
            ) VALUES (?,?,?,?,?,?,?,?,?,?)
            """,
            (
                uid,
                q.get("question"),
                q.get("option_a"),
                q.get("option_b"),
                q.get("option_c"),
                q.get("option_d"),
                q.get("correct"),
                q.get("source"),
                int(time.time()),
                0,
            ),
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def pick_unused_question(db_path: str = DB_PATH) -> Optional[Dict]:
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute(
        "SELECT id, question, option_a, option_b, option_c, option_d, correct FROM questions WHERE used=0 ORDER BY RANDOM() LIMIT 1"
    )
    row = c.fetchone()
    conn.close()
    if row:
        return {
            "id": row[0],
            "question": row[1],
            "option_a": row[2],
            "option_b": row[3],
            "option_c": row[4],
            "option_d": row[5],
            "correct": row[6],
        }
    return None


def mark_used(question_id: int, db_path: str = DB_PATH) -> None:
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("UPDATE questions SET used=1 WHERE id=?", (question_id,))
    conn.commit()
    conn.close()

# ------------------- Fetch / Parse -------------------

def parse_example_site(html: str) -> List[Dict]:
    """ÖRNEK: Hedef sitenizin HTML yapısına göre özelleştirin."""
    soup = BeautifulSoup(html, "html.parser")
    items: List[Dict] = []
    for block in soup.select(".question-block"):
        q_text_el = block.select_one(".q-text")
        if not q_text_el:
            continue
        q_text = q_text_el.get_text(strip=True)
        opts = block.select(".option")
        opt_texts = [o.get_text(strip=True) for o in opts]
        item: Dict[str, Optional[str]] = {
            "question": q_text,
            "option_a": opt_texts[0] if len(opt_texts) > 0 else None,
            "option_b": opt_texts[1] if len(opt_texts) > 1 else None,
            "option_c": opt_texts[2] if len(opt_texts) > 2 else None,
            "option_d": opt_texts[3] if len(opt_texts) > 3 else None,
            "correct": None,
            "source": "example_test_site",
        }
        items.append(item)
    return items


SOURCES: List[Dict[str, str]] = [
    {"name": "example_test_site", "url": "https://example.com/traffic-questions"}
]


def fetch_source(url: str, headers: Optional[Dict[str, str]] = None) -> Optional[str]:
    try:
        resp = requests.get(url, headers=headers or DEFAULT_HEADERS, timeout=REQUEST_TIMEOUT_SECONDS)
        if resp.status_code == 200:
            return resp.text
        print(f"[fetch] Kaynağa erişilemedi: {url} status={resp.status_code}")
    except Exception as exc:
        print(f"[fetch] İstek hatası: {url} error={exc}")
    return None


def fetch_and_store_all(db_path: str = DB_PATH) -> None:
    init_db(db_path)
    total_added = 0
    for src in SOURCES:
        html = fetch_source(src["url"])
        if not html:
            continue
        try:
            questions = parse_example_site(html)
        except Exception as exc:
            print("[fetch] Parse hatası:", exc)
            continue
        for q in questions:
            if insert_question(db_path, q):
                total_added += 1
    print(f"Eklenen yeni soru: {total_added}")

# ------------------- Görsel/Video Üretimi -------------------

def _load_font(size: int) -> ImageFont.FreeTypeFont:
    candidates = [
        FONT_PATH,
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for path in candidates:
        if path and os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def render_question_image(q: Dict, out_path: str) -> str:
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img = Image.new("RGB", IMG_SIZE, color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    title_font = _load_font(72)
    body_font = _load_font(52)

    w, h = IMG_SIZE

    # Soru metni
    question = q.get("question", "").strip()
    wrapped_lines = textwrap.wrap(question, width=24)
    current_y = 260
    for line in wrapped_lines:
        tw, th = draw.textsize(line, font=title_font)
        draw.text(((w - tw) / 2, current_y), line, fill=(0, 0, 0), font=title_font)
        current_y += th + 12

    # Ok ve seçenekler
    option_box_top = h - 560
    arrow_y = option_box_top - 40
    arrow_x = int(w * 0.1)
    draw.polygon(
        [
            (arrow_x, arrow_y),
            (arrow_x + 48, arrow_y - 36),
            (arrow_x + 48, arrow_y + 36),
        ],
        fill=(0, 0, 0),
    )

    opt_x = int(w * 0.22)
    opt_y = option_box_top
    spacing = 86
    options = [q.get("option_a"), q.get("option_b"), q.get("option_c"), q.get("option_d")]
    options = [o for o in options if o]
    for i, opt in enumerate(options):
        txt = f"{chr(65 + i)}) {opt}"
        draw.text((opt_x, opt_y + i * spacing), txt, fill=(0, 0, 0), font=body_font)

    img.save(out_path, quality=95)
    return out_path


def make_reel_for_question_return_paths(q: Dict, duration_seconds: int = 6, out_video_path: Optional[str] = None) -> Tuple[str, str]:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    fname = f"reel_{q['id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    img_path = os.path.join(OUTPUT_DIR, f"{fname}.jpg")
    render_question_image(q, img_path)

    clip = ImageClip(img_path).set_duration(duration_seconds)
    clip = clip.resize(width=1080)

    if not out_video_path:
        out_video_path = os.path.join(OUTPUT_DIR, f"{fname}.mp4")
    try:
        clip.write_videofile(
            out_video_path,
            fps=24,
            codec="libx264",
            audio=False,
            verbose=False,
            logger=None,
        )
    except Exception as exc:
        raise RuntimeError(f"Video yazma hatası: {exc}")

    return out_video_path, img_path

# ------------------- Instagram Uploaders -------------------

def _ensure_file_dir(path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)


def upload_reel(video_path: str, caption: Optional[str] = None) -> None:
    if os.environ.get("DRY_RUN") == "1":
        print(f"[DRY_RUN] Reel atlandı. Video: {video_path}\nCaption:\n{caption}")
        return
    if not USERNAME or not PASSWORD:
        raise ValueError("IG_USERNAME ve IG_PASSWORD çevre değişkenlerini tanımlayın.")
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video dosyası bulunamadı: {video_path}")

    from instagrapi import Client

    cl = Client()

    if os.path.exists(SESSION_PATH):
        try:
            with open(SESSION_PATH, "r", encoding="utf-8") as f:
                settings = json.load(f)
            cl.set_settings(settings)
        except Exception:
            pass

    cl.login(USERNAME, PASSWORD)

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


def upload_story_with_interaction(image_path: str, question_text: str, options: List[str], correct_index: Optional[int] = None, caption: Optional[str] = None) -> None:
    if os.environ.get("DRY_RUN") == "1":
        print(f"[DRY_RUN] Story atlandı. Görsel: {image_path}\nSoru: {question_text}\nSeçenekler: {options}\nCaption: {caption}")
        return
    if not USERNAME or not PASSWORD:
        raise ValueError("IG_USERNAME ve IG_PASSWORD çevre değişkenlerini tanımlayın.")
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Görsel dosyası bulunamadı: {image_path}")

    from instagrapi import Client

    cl = Client()

    if os.path.exists(SESSION_PATH):
        try:
            with open(SESSION_PATH, "r", encoding="utf-8") as f:
                settings = json.load(f)
            cl.set_settings(settings)
        except Exception:
            pass

    cl.login(USERNAME, PASSWORD)

    try:
        _ensure_file_dir(SESSION_PATH)
        with open(SESSION_PATH, "w", encoding="utf-8") as f:
            json.dump(cl.get_settings(), f)
    except Exception:
        pass

    try:
        sticker = None
        try:
            from instagrapi.types import StorySticker, StoryQuiz, StoryPoll
            if isinstance(correct_index, int) and 0 <= correct_index < len(options) and 2 <= len(options) <= 4:
                try:
                    core = StoryQuiz(question=question_text, options=options, correct_answer=correct_index)
                    sticker = StorySticker(sticker=core, x=0.5, y=0.78, width=0.85, height=0.22, rotation=0.0)
                except Exception:
                    sticker = None
            if sticker is None and len(options) >= 2:
                try:
                    core = StoryPoll(question=question_text, options=options[:2])
                    sticker = StorySticker(sticker=core, x=0.5, y=0.78, width=0.85, height=0.22, rotation=0.0)
                except Exception:
                    sticker = None
        except Exception:
            sticker = None

        if sticker is not None:
            media = cl.photo_upload_to_story(image_path, caption=caption, stickers=[sticker])
        else:
            media = cl.photo_upload_to_story(image_path, caption=caption)
        print("Story yüklendi. media id:", getattr(media, "pk", None))
    except Exception as e:
        print("Story upload failed:", e)
        raise
    finally:
        try:
            cl.logout()
        except Exception:
            pass

# ------------------- Orkestrasyon -------------------

def _build_caption(q: dict) -> str:
    options = [q.get("option_a"), q.get("option_b"), q.get("option_c"), q.get("option_d")]
    options = [o for o in options if o]
    lines = [q.get("question", "")] + [f"{chr(65 + i)}) {opt}" for i, opt in enumerate(options)]
    return "\n".join(lines)


def _build_story_params(q: dict) -> Tuple[str, List[str], Optional[int]]:
    question_text = q.get("question", "")
    options = [o for o in [q.get("option_a"), q.get("option_b"), q.get("option_c"), q.get("option_d")] if o]
    correct_letter = (q.get("correct") or "").strip().upper()
    correct_index = None
    if correct_letter in {"A", "B", "C", "D"}:
        idx = ord(correct_letter) - ord("A")
        if 0 <= idx < len(options):
            correct_index = idx
    return question_text, options, correct_index


def run_once() -> Optional[str]:
    try:
        fetch_and_store_all()
    except Exception as e:
        print("Fetch error:", e)

    q = pick_unused_question()
    if not q:
        print("No unused question available.")
        return None

    try:
        video_path, image_path = make_reel_for_question_return_paths(q)
    except Exception as e:
        print("Make reel error:", e)
        return None

    caption = _build_caption(q)

    try:
        upload_reel(video_path, caption=caption)
    except Exception as e:
        print("Upload error:", e)
    else:
        try:
            mark_used(q["id"])
        except Exception as e:
            print("Mark used error:", e)

        # Story (quiz/poll)
        try:
            question_text, options, correct_index = _build_story_params(q)
            story_caption = None
            upload_story_with_interaction(
                image_path=image_path,
                question_text=question_text,
                options=options,
                correct_index=correct_index,
                caption=story_caption,
            )
        except Exception as e:
            print("Story upload error:", e)

    return video_path

# ------------------- Seed -------------------
SAMPLE_QUESTIONS: List[Dict] = [
    {
        "question": "Işıklı trafik işaret cihazında kırmızı ışık yanıyorsa ne yapılmalıdır?",
        "option_a": "Durulmalı ve beklenmeli",
        "option_b": "Hız azaltılarak dikkatli geçilmeli",
        "option_c": "Yaya yoksa geçilmeli",
        "option_d": "Sadece sağa dönüş yapılmalı",
        "correct": "A",
        "source": "seed",
    },
    {
        "question": "Aşağıdakilerden hangisi geçiş üstünlüğüne sahiptir?",
        "option_a": "Toplu taşıma araçları",
        "option_b": "İtfaiye aracı",
        "option_c": "Okul servisi",
        "option_d": "Taksi",
        "correct": "B",
        "source": "seed",
    },
    {
        "question": "Yerleşim yeri içinde iki yönlü karayolunda azami hız sınırı binek araçlar için kaç km/saattir?",
        "option_a": "30",
        "option_b": "50",
        "option_c": "70",
        "option_d": "90",
        "correct": "B",
        "source": "seed",
    },
    {
        "question": "Aşağıdakilerden hangisi araçta bulundurulması zorunlu değilidir?",
        "option_a": "İlk yardım çantası",
        "option_b": "Yangın söndürücü",
        "option_c": "Stepne",
        "option_d": "Kar zinciri (yaz mevsimi)",
        "correct": "D",
        "source": "seed",
    },
    {
        "question": "Şerit değiştirmeden önce ilk yapılması gereken işlem nedir?",
        "option_a": "Sinyal vermek",
        "option_b": "Omuz üstü kontrol yapmak",
        "option_c": "Ayna kontrolü yapmak",
        "option_d": "Hızlanmak",
        "correct": "C",
        "source": "seed",
    },
]


def seed(db_path: str = DB_PATH) -> int:
    init_db(db_path)
    added = 0
    for q in SAMPLE_QUESTIONS:
        if insert_question(db_path, q):
            added += 1
    print(f"Eklendi: {added} soru (seed)")
    return added

# ------------------- Scheduler -------------------

def start_scheduler() -> None:
    scheduler = BlockingScheduler(timezone=TZ)

    def fetch_job() -> None:
        print("[FETCH JOB BAŞLADI]", datetime.now(TZ))
        try:
            fetch_and_store_all()
        except Exception as exc:
            print("[FETCH JOB HATA]", exc)
        print("[FETCH JOB BİTTİ]", datetime.now(TZ))

    def post_job() -> None:
        print("[POST JOB BAŞLADI]", datetime.now(TZ))
        try:
            run_once()
        except Exception as exc:
            print("[POST JOB HATA]", exc)
        print("[POST JOB BİTTİ]", datetime.now(TZ))

    scheduler.add_job(fetch_job, CronTrigger(hour=3, minute=0))
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

# ------------------- CLI -------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Tek dosya Instagram Trafik Test Botu")
    sub = parser.add_subparsers(dest="command")
    sub.required = False

    sub.add_parser("run-once", help="Tek seferlik paylaşım akışı")
    sub.add_parser("seed", help="Veritabanına örnek sorular ekle")
    sub.add_parser("scheduler", help="APScheduler ile otomatik çalışma")
    sub.add_parser("fetch-only", help="Sadece soru çek/güncelle")

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cmd = args.command or "run-once"

    if cmd == "run-once":
        run_once()
    elif cmd == "seed":
        seed()
    elif cmd == "scheduler":
        start_scheduler()
    elif cmd == "fetch-only":
        fetch_and_store_all()
    else:
        print("Bilinmeyen komut")


if __name__ == "__main__":
    main()