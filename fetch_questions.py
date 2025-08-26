"""
Sorumluluk: Kaynak(lar)dan yeni soruları çeker ve SQLite veritabanına ekler.
- Yapı: configurable kaynak listesi (URL'ler veya API endpoint'leri)
- Her kaynaktan çekilen ham veri için parse_function yazılmalıdır.
- Duplicate kontrolü: soruların hash'i/benzersiz ID'si DB'de saklanır.
"""

import os
import time
import hashlib
import sqlite3
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "questions.db")

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/118.0 Safari/537.36"
)
DEFAULT_HEADERS = {"User-Agent": USER_AGENT}
REQUEST_TIMEOUT_SECONDS = 20


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


# ---------- Example scraper/parsers ----------

def parse_example_site(html: str) -> List[Dict]:
    """
    NOT: Bu örnek, hedef sitenize göre özelleştirilmeli. CSS seçimleri placeholder'dır.
    """
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
    {
        "name": "example_test_site",
        "url": "https://example.com/traffic-questions",
    }
]


def fetch_source(url: str, headers: Optional[Dict[str, str]] = None) -> Optional[str]:
    try:
        resp = requests.get(url, headers=headers or DEFAULT_HEADERS, timeout=REQUEST_TIMEOUT_SECONDS)
        if resp.status_code == 200:
            return resp.text
        print(f"[fetch_questions] Kaynağa erişilemedi: {url} status={resp.status_code}")
    except Exception as exc:
        print(f"[fetch_questions] İstek hatası: {url} error={exc}")
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
            print("[fetch_questions] Parse hatası:", exc)
            continue
        for q in questions:
            added = insert_question(db_path, q)
            if added:
                total_added += 1
    print(f"Eklenen yeni soru: {total_added}")


if __name__ == "__main__":
    fetch_and_store_all()