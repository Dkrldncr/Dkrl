# Trafik Reels Botu (Tam Otomatik)

Günlük saatlerde (08:00, 11:00, 13:00, 18:00, 22:00) otomatik olarak soru tabanlı kısa Reels videoları üretip Instagram'a yükler. Sorular internetten toplanır (örnek parser iskeleti) ve SQLite veritabanında saklanır.

## Gereksinimler

- Python 3.10+
- FFmpeg (moviepy için gerekli) — Linux'ta: `sudo apt-get install ffmpeg`
- Bağımlılıklar:

```bash
pip install -r requirements.txt
```

## Ortam Değişkenleri

- `IG_USERNAME` ve `IG_PASSWORD`: Instagram hesabı bilgileri
- `DRY_RUN=1`: Yükleme adımını atlar (test için)
- `TZ=Europe/Istanbul`: Zaman dilimi (scheduler için)
- `FONT_PATH=/path/to/SomeSans.ttf`: Özel font kullanmak isterseniz

## Başlangıç

1) Veritabanını başlat ve örnek soruları ekle (opsiyonel ama önerilir):

```bash
python seed_questions.py
```

2) Tek seferlik akış (fetch -> make -> upload):

```bash
export IG_USERNAME=xxxxx
export IG_PASSWORD=xxxxx
python main.py
```

3) Sürekli çalışma (APScheduler):

```bash
export IG_USERNAME=xxxxx
export IG_PASSWORD=xxxxx
python scheduler.py
```

- Otomatik işler:
  - 03:00: Kaynaklardan soru çekme/güncelleme
  - 08:00, 11:00, 13:00, 18:00, 22:00: Reels üretme ve yükleme

## Dosyalar

- `fetch_questions.py`: Soruları internetten çekip `questions.db` içine yazar. Mevcut `parse_example_site` örnek amaçlıdır; hedef kaynağa göre özelleştiriniz.
- `make_reel.py`: DB'den kullanılmamış bir soru seçer, Pillow ile görsel + MoviePy ile video üretir.
- `post_reel.py`: Instagrapi ile Reels yükler. `DRY_RUN=1` ile deneme yapabilirsiniz.
- `main.py`: Tek seferlik orkestrasyon.
- `scheduler.py`: Belirli saatlerde otomatik çalıştırma.
- `seed_questions.py`: Test için 20 soru ekler.

## Notlar / Uyarılar

- Hedef sitelerin kullanım şartlarına ve telif haklarına uyun. Scraping kısmını yasal çerçevede, robots.txt ve izinlere uygun yapınız.
- Instagram otomasyonu hassastır. 2FA, IP değişimi, cihaz parmak izi gibi kontroller olabilir. `instagrapi_settings.json` oturum kalıcılığı için kullanılır.
- Reels'e anket sticker API kısıtları nedeniyle doğrudan eklemek mümkün olmayabilir. Alternatif: Story'de poll sticker veya Reels açıklamasına soru/seçenekleri eklemek.
- FFmpeg kurulu değilse video yazma aşaması hata verir.