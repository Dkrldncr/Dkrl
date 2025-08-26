## Trafik Reels Botu (Tam Otomatik)

Güncel trafik/e-sınav sorularını toplayıp her gün 08:00, 11:00, 13:00, 18:00, 22:00 saatlerinde Instagram Reels olarak paylaşır. Sorular SQLite DB'de saklanır ve paylaşılanlar işaretlenir.

### Gereksinimler
- Python 3.10+
- FFmpeg (moviepy için gerekli)

Paketler:
```
pip install -r requirements.txt
```

### Ortam Değişkenleri
- `IG_USERNAME`: Instagram kullanıcı adı
- `IG_PASSWORD`: Instagram şifresi
- (opsiyonel) `PYTHON_BIN`: scheduler'ın çağıracağı Python (varsayılan `python3`)

Linux örneği:
```
export IG_USERNAME="kullanici"
export IG_PASSWORD="sifre"
```

### İlk Kurulum
1. Bağımlılıkları yükleyin: `pip install -r requirements.txt`
2. Veritabanını başlatın ve (isteğe bağlı) örnek soruları ekleyin:
```
python fetch_questions.py   # tabloyu oluşturur, örnek kaynak isteği atar
python seed_questions.py    # 20 örnek soru ekler (test amaçlı)
```

### Tek Seferlik Çalıştırma
```
python main.py
```
- Akış: Soruları günceller → 1 soru seçer → JPG/MP4 üretir → Reels yükler → soruyu `used=1` yapar.

### Zamanlayıcı (Sürekli Çalışma)
```
python scheduler.py
```
- 03:00: Soruları çeker/günceller
- 08:00, 11:00, 13:00, 18:00, 22:00: Reels paylaşır

### Notlar ve Uyarılar
- Scraper kısmındaki `fetch_questions.py` içeriği örnektir. Hedef sitenin izinleri ve TOS'a uygunluk sizdedir. Gerekli parse fonksiyonlarını siteye göre özelleştirin.
- Instagrapi ve Instagram davranışları değişebilir. Gerekirse 2FA, session dosyası vb. eklemek mümkündür.
- MoviePy için sisteminizde FFmpeg kurulu olmalıdır. Ubuntu: `sudo apt-get install ffmpeg`
- Telif haklarına ve kişisel veri kurallarına uyun.