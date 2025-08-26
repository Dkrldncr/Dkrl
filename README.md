# Kural Tabanlı Sohbet Asistanı

Bu proje, paylaşılan ChatGPT sohbetinden (veya sizin yapıştıracağınız metinden) kuralları alıp, OpenAI destekli bir sohbet asistanı oluşturur. Streamlit ile hızlıca çalıştırabilirsiniz.

## Kurulum

1) Depoyu/klasörü hazırlayın ve bağımlılıkları kurun:

```bash
cd /workspace
python3 -m venv .venv
/workspace/.venv/bin/python -m pip install -U pip
/workspace/.venv/bin/pip install -r requirements.txt
```

2) Ortam değişkenlerini ayarlayın:

```bash
cp .env.example .env
# .env dosyasını düzenleyip OPENAI_API_KEY değerini girin
```

## Çalıştırma

```bash
/workspace/.venv/bin/streamlit run src/app.py
```

Tarayıcıda açılan arayüzde:
- Paylaşılan ChatGPT bağlantısını girip "Kuralları Yükle"ye tıklayabilir veya
- Doğrudan kuralları metin olarak yapıştırabilirsiniz.

Ardından, sohbet alanından asistanla konuşabilirsiniz.

## Notlar
- Paylaşılan ChatGPT bağlantıları zaman zaman dinamik (JS) içerik sunabilir. Bu durumda sayfa içeriği otomatik çekilemeyebilir. Böyle bir durumda kuralları metin olarak yapıştırma yolunu kullanabilirsiniz.
- Model varsayılanı `gpt-4o-mini`'dir. `.env` içinde `OPENAI_MODEL` ile değiştirebilirsiniz.