import re
from typing import Optional
import requests
from bs4 import BeautifulSoup


_DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
    "Cache-Control": "no-cache",
}


def _normalize_whitespace(text: str) -> str:
    text = re.sub(r"\r\n|\r|\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"\t", "\t", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()


def _extract_text_from_html(html: str, max_chars: int = 50000) -> str:
    soup = BeautifulSoup(html, "html.parser")

    # Prefer <article> if exists
    article = soup.find("article")
    if article:
        text = article.get_text("\n", strip=True)
        return _normalize_whitespace(text)[:max_chars]

    # Fallback to main content
    main = soup.find("main")
    if main:
        text = main.get_text("\n", strip=True)
        return _normalize_whitespace(text)[:max_chars]

    # Last resort: whole page text
    text = soup.get_text("\n", strip=True)
    return _normalize_whitespace(text)[:max_chars]


def fetch_shared_link(url: str, timeout_seconds: int = 15) -> str:
    if not url or not url.startswith("http"):
        raise ValueError("Geçerli bir URL girin.")

    try:
        response = requests.get(url, headers=_DEFAULT_HEADERS, timeout=timeout_seconds)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise ValueError(f"Bağlantı alınamadı: {exc}") from exc

    # Some shared links may return minimal shells; still attempt to parse
    return _extract_text_from_html(response.text)


def load_rules_from_url(url: str) -> str:
    """Loads rules text from a ChatGPT shared link or any HTML page.

    Returns cleaned text. Raises ValueError on failure.
    """
    text = fetch_shared_link(url)
    if not text or len(text) < 20:
        raise ValueError("Sayfadan anlamlı metin çıkarılamadı. Lütfen kuralları metin olarak yapıştırın.")
    return text