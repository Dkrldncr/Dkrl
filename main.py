"""
Orkestrasyon: Aşağıdaki akışı uygular:
1) fetch_questions.fetch_and_store_all()
2) make_reel.pick_unused_question() -> make_reel.make_reel_for_question()
3) post_reel.upload_reel()
4) make_reel.mark_used()

Bu script'i iki şekilde çalıştırabilirsiniz:
- Zamanlayıcı ile belirli saatlerde tetiklemek (08:00,11:00,13:00,18:00,22:00)
- Veya tek seferlik
"""

import os
from typing import Optional

from fetch_questions import fetch_and_store_all
from make_reel import pick_unused_question, make_reel_for_question, mark_used
from post_reel import upload_reel
from post_reel import upload_story_with_interaction
from make_reel import make_reel_for_question_return_paths


def _build_caption(q: dict) -> str:
    options = [q.get("option_a"), q.get("option_b"), q.get("option_c"), q.get("option_d")]
    options = [o for o in options if o]
    lines = [q.get("question", "")] + [f"{chr(65 + i)}) {opt}" for i, opt in enumerate(options)]
    return "\n".join(lines)


def _build_story_params(q: dict):
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
    # 1 - Güncel soruları çek
    try:
        fetch_and_store_all()
    except Exception as e:
        print("Fetch error:", e)

    # 2 - DB'den bir soru al
    q = pick_unused_question()
    if not q:
        print("No unused question available.")
        return None

    # 3 - Reel oluştur
    try:
        video_path, image_path = make_reel_for_question_return_paths(q)
    except Exception as e:
        print("Make reel error:", e)
        return None

    # 4 - Caption hazırla (soru + seçenekleri)
    caption = _build_caption(q)

    # 5 - Yükle
    try:
        upload_reel(video_path, caption=caption)
    except Exception as e:
        print("Upload error:", e)
    else:
        # 6 - Mark used
        try:
            mark_used(q["id"])
        except Exception as e:
            print("Mark used error:", e)

        # 7 - Story (quiz/poll) paylaşımı
        try:
            question_text, options, correct_index = _build_story_params(q)
            story_caption = None  # Görüntü üzerinde zaten metin var; isterseniz caption ekleyin
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


if __name__ == "__main__":
    run_once()