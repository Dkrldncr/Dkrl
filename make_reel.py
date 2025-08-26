"""
Sorumluluk: DB'den 'used=0' olan sorulardan birini seçer ve görsel/video üretir.
- Beyaz fon üzerinde siyah yazı: soru ortada
- Alt kısımda ok ile işaretleyerek seçenekleri gösterir (sağda)
- MoviePy ile kısa video oluşturur
"""

import os
import sqlite3
import textwrap
from datetime import datetime
from typing import Dict, Optional

from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageClip

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "questions.db")
OUTPUT_DIR = os.path.join(BASE_DIR, "output_reels")
IMG_SIZE = (1080, 1920)

# Font konfigürasyonu: Çevre değişkeni FONT_PATH ile özelleştirilebilir
FONT_PATH = os.environ.get("FONT_PATH")


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
    # Fallback
    return ImageFont.load_default()


def pick_unused_question(db_path: str = DB_PATH) -> Optional[Dict]:
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute(
        "SELECT id, question, option_a, option_b, option_c, option_d FROM questions WHERE used=0 ORDER BY RANDOM() LIMIT 1"
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
        }
    return None


def mark_used(question_id: int, db_path: str = DB_PATH) -> None:
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("UPDATE questions SET used=1 WHERE id=?", (question_id,))
    conn.commit()
    conn.close()


def render_question_image(q: Dict, out_path: str) -> str:
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    img = Image.new("RGB", IMG_SIZE, color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    title_font = _load_font(72)
    body_font = _load_font(52)

    w, h = IMG_SIZE

    # Soru metni: ortalanmış ve satıra bölünmüş
    question = q.get("question", "").strip()
    wrapped_lines = textwrap.wrap(question, width=24)
    current_y = 260
    for line in wrapped_lines:
        tw, th = draw.textsize(line, font=title_font)
        draw.text(((w - tw) / 2, current_y), line, fill=(0, 0, 0), font=title_font)
        current_y += th + 12

    # Seçenekler kutusu
    option_box_top = h - 560
    arrow_y = option_box_top - 40

    # Basit ok (sol taraftan sağa doğru)
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


def make_reel_for_question_return_paths(q: Dict, duration_seconds: int = 6, out_video_path: Optional[str] = None) -> (str, str):
    """
    Video ve görseli üretir ve (video_path, image_path) olarak döner.
    """
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


def make_reel_for_question(q: Dict, duration_seconds: int = 6, out_video_path: Optional[str] = None) -> str:
    video_path, _img_path = make_reel_for_question_return_paths(q, duration_seconds, out_video_path)
    return video_path


if __name__ == "__main__":
    q = pick_unused_question()
    if q:
        vp = make_reel_for_question(q)
        print("Created video:", vp)
        mark_used(q["id"])
    else:
        print("No unused questions found.")