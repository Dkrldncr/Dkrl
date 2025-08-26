# Starter API (FastAPI + SQLModel + JWT)

Bu depo, üretim için uygun, JWT kimlik doğrulamalı, SQLModel (SQLite) veritabanlı bir FastAPI başlangıç projesi sağlar.

## Kurulum

1) Python 3.11+ kurulu olmalıdır. 
2) Bağımlılıkları yükleyin:

```bash
pip install -r requirements.txt
```

3) Uygulamayı başlatın:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

4) API dokümantasyonu: `http://localhost:8000/docs`

## Ortam Değişkenleri
- `SECRET_KEY`: JWT imza anahtarı (varsayılan: `change-me-please`)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token süresi (dakika) (varsayılan: `60`)
- `ALGORITHM`: JWT algoritması (varsayılan: `HS256`)
- `DATABASE_URL`: Veritabanı URL (varsayılan: `sqlite:///./app.db`)
- `CORS_ORIGINS`: CORS izinli origin listesi (virgülle ayrılmış)

## Uç Noktalar
- `POST /auth/register`: Yeni kullanıcı kaydı
- `POST /auth/login`: Giriş (OAuth2 Password) -> `access_token`
- `GET /projects/`: Proje listele (Bearer Token gerekli)
- `POST /projects/`: Proje oluştur (Bearer Token gerekli)
- `GET /projects/{id}`: Proje getir (Bearer Token gerekli)
- `PUT /projects/{id}`: Proje güncelle (Bearer Token gerekli)
- `DELETE /projects/{id}`: Proje sil (Bearer Token gerekli)

## Test
```bash
pytest -q
```