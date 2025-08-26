"""
Sorumluluk: DB'den 'used=0' olan sorulardan 1 veya istenen sayıda seçer, her soru için:
 - Beyaz fon üzerinde siyah yazı: soru ortada
 - Alt kısımda ok ile işaretleyerek seçenekleri gösterir (sağda)
 - Birkaç saniyelik kısa video oluşturur (MoviePy)
 - Video dosyasını output klasörüne kaydeder
"""

from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageClip
import sqlite3
import os
import textwrap
from datetime import datetime

DB_PATH = "questions.db"
OUTPUT_DIR = "output_reels"
FONT_PATH = None  # isteğe göre bir TTF yolu verin
IMG_SIZE = (1080, 1920)


def pick_unused_question(db_path: str = DB_PATH):
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


essential_fonts_loaded = False

def _load_fonts():
    global essential_fonts_loaded
    try:
        if FONT_PATH and os.path.exists(FONT_PATH):
            title_font = ImageFont.truetype(FONT_PATH, 80)
            body_font = ImageFont.truetype(FONT_PATH, 56)
        else:
            title_font = ImageFont.load_default()
            body_font = ImageFont.load_default()
        essential_fonts_loaded = True
        return title_font, body_font
    except Exception:
        essential_fonts_loaded = False
        return ImageFont.load_default(), ImageFont.load_default()


def render_question_image(q: dict, out_path: str) -> str:
    img = Image.new("RGB", IMG_SIZE, color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    title_font, body_font = _load_fonts()

    w, h = IMG_SIZE

    # Draw question (wrapped, centered)
    question = q["question"]
    wrapped = textwrap.wrap(question, width=30)
    current_h = 200
    for line in wrapped:
        tw, th = draw.textsize(line, font=title_font)
        draw.text(((w - tw) / 2, current_h), line, fill=(0, 0, 0), font=title_font)
        current_h += th + 10

    # Draw options at bottom with arrow pointing
    option_box_top = h - 540
    arrow_y = option_box_top - 40

    # simple arrow (triangle)
    arrow_x = int(w * 0.1)
    draw.polygon(
        [(arrow_x, arrow_y), (arrow_x + 40, arrow_y - 30), (arrow_x + 40, arrow_y + 30)],
        fill=(0, 0, 0),
    )

    opt_x = int(w * 0.2)
    opt_y = option_box_top
    spacing = 80
    options = [q.get("option_a"), q.get("option_b"), q.get("option_c"), q.get("option_d")]
    options = [o for o in options if o]
    for i, opt in enumerate(options):
        txt = f"{chr(65 + i)}) {opt}"
        draw.text((opt_x, opt_y + i * spacing), txt, fill=(0, 0, 0), font=body_font)

    img.save(out_path, quality=95)
    return out_path


def make_reel_for_question(q: dict, duration_per_frame: int = 5, out_video_path: str = None) -> str:
    # Render image
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    fname = f"reel_{q['id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    img_path = os.path.join(OUTPUT_DIR, fname)
    render_question_image(q, img_path)

    # Make video clip from image
    clip = ImageClip(img_path).set_duration(duration_per_frame)
    clip = clip.resize(width=1080)

    # Write video
    if not out_video_path:
        out_video_path = img_path.replace(".jpg", ".mp4")
    # Disable verbose logging to keep stdout clean
    clip.write_videofile(
        out_video_path,
        fps=24,
        codec="libx264",
        audio=False,
        verbose=False,
        logger=None,
    )
    return out_video_path


if __name__ == "__main__":
    q = pick_unused_question()
    if q:
        vp = make_reel_for_question(q)
        print("Created video:", vp)
        mark_used(q["id"])
    else:
        print("No unused questions found.")