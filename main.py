"""
Orkestrasyon: Aşağıdaki akışı uygular:
1) fetch_questions.fetch_and_store_all()
2) make_reel.pick_unused_question() -> make_reel.make_reel_for_question()
3) post_reel.upload_reel()
4) make_reel.mark_used()
"""

from fetch_questions import fetch_and_store_all
from make_reel import pick_unused_question, make_reel_for_question, mark_used
from post_reel import upload_reel


def run_once() -> None:
    # 1 - Güncel soruları çek
    try:
        fetch_and_store_all()
    except Exception as e:
        print("Fetch error:", e)

    # 2 - DB'den bir soru al
    q = pick_unused_question()
    if not q:
        print("No unused question available.")
        return

    # 3 - Reel oluştur
    try:
        video_path = make_reel_for_question(q)
    except Exception as e:
        print("Make reel error:", e)
        return

    # 4 - Caption hazırla (soru + seçenekleri)
    options = [q.get("option_a"), q.get("option_b"), q.get("option_c"), q.get("option_d")]
    options = [o for o in options if o]
    caption_lines = [q.get("question")] + [f"{chr(65 + i)}) {opt}" for i, opt in enumerate(options)]
    caption = "\n".join(caption_lines)

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


if __name__ == "__main__":
    run_once()