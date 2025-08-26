"""
Sorumluluk: Kaynak(lar)dan yeni soruları çeker ve SQLite veritabanına ekler.
- Yapı: configurable kaynak listesi (URL'ler veya API endpoint'leri)
- Her kaynaktan çekilen ham veri için parse_function yazılmalıdır.
- Duplicate kontrolü: soruların hash'i/benzersiz ID'si DB'de saklanır.
"""

import sqlite3
import requests
from bs4 import BeautifulSoup
import hashlib
from typing import List, Dict
import time

DB_PATH = "questions.db"

# Örnek kaynak - hedef siteye göre özelleştirin.
SOURCES = [
    {
        "name": "example_test_site",
        "url": "https://example.com/traffic-questions",
        # parse fonksiyonu aşağıda, gerçek siteye göre düzenleyin
    },
]

# ---------- DB helpers ----------

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


def question_uid(question_text: str, options: List[str]) -> str:
    normalized = question_text.strip() + "||" + "||".join([o.strip() for o in options if o])
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def insert_question(db_path: str, q: Dict) -> bool:
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    try:
        uid = question_uid(
            q["question"],
            [
                q.get("option_a", ""),
                q.get("option_b", ""),
                q.get("option_c", ""),
                q.get("option_d", ""),
            ],
        )
        c.execute(
            """
            INSERT INTO questions
            (uid, question, option_a, option_b, option_c, option_d, correct, source, fetched_at, used)
            VALUES (?,?,?,?,?,?,?,?,?,?)
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
        # duplicate
        return False
    finally:
        conn.close()


# ---------- Example scraper/parsers ----------

def parse_example_site(html: str) -> List[Dict]:
    # NOT: Bu örnek, hedef sitenize göre özelleştirilmeli.
    soup = BeautifulSoup(html, "html.parser")
    items: List[Dict] = []
    for block in soup.select(".question-block"):
        q_text_node = block.select_one(".q-text")
        if not q_text_node:
            continue
        q_text = q_text_node.get_text(strip=True)
        opts = block.select(".option")
        opt_texts = [o.get_text(strip=True) for o in opts]
        item = {
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


def fetch_and_store_all(db_path: str = DB_PATH) -> None:
    init_db(db_path)

    # Basit tek kaynak örneği; çoklu kaynaklar için döngü ile genişletin
    src = SOURCES[0]
    try:
        r = requests.get(src["url"], timeout=20)
    except Exception as e:
        print("Kaynağa istek hatası:", e)
        return

    if r.status_code == 200:
        questions = parse_example_site(r.text)
        added = 0
        for q in questions:
            if insert_question(db_path, q):
                added += 1
        print(f"Eklenen yeni soru: {added}")
    else:
        print("Kaynağa bağlanılamadı:", src["url"], r.status_code)


if __name__ == "__main__":
    fetch_and_store_all()