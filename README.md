# Üniversite Kütüphanesi Yapay Zeka Asistanı

Batman Üniversitesi Kütüphanesi için geliştirilmiş sohbet tabanlı asistan. Kullanıcı doğal dille soru sorar; sistem kütüphane kataloğunu, akademik arşivi ve kütüphane web sitesini tarayıp yanıtı Türkçe ve düzenli biçimde döndürür.

> Bu depo, özel bir müşteri için yapılan çalışmanın genelleştirilmiş sürümüdür.

## Çözdüğü problem

Öğrenci ve akademisyenler kaynağı bulmak için katalog, tez arşivi ve duyuru sayfaları arasında dolaşır. Asistan bu üç kaynağı tek bir sohbet kutusunda birleştirir.

## Özellikler

- Katalog araması: Yordam kütüphane otomasyonunun web servisi üzerinden kitap ve dergi sorgulama.
- Akademik arşiv: OAI-PMH protokolüyle kurumsal arşivden (tez, makale vb.) üst veri çekme.
- Kütüphane bilgisi: web sitesinden duyuruları, personel listesini ve iletişim bilgilerini çekme.
- Yapay zeka yanıtı: LangChain ve OpenAI ile Türkçe, başlık-yazar-tarih biçiminde düzenli yanıt.
- Basit web arayüzü (Jinja2 şablonları).

## Teknoloji yığını

Python, FastAPI, Jinja2, LangChain, OpenAI API, Requests, BeautifulSoup, Sickle (OAI-PMH).

## Proje yapısı

```
kutuphane-sistem/
├── app.py                    FastAPI uygulaması (GET /, POST /sorgula, GET /bilgiler)
├── integrations/
│   ├── query_service.py      Sorguyu doğru kaynağa yönlendirir
│   ├── library_api.py        Yordam katalog servisi
│   ├── oai_pmh.py            Akademik arşiv (OAI-PMH)
│   ├── web_scraper.py        Duyuru, personel, iletişim
│   ├── yordam_token_manager.py
│   └── chatgpt.py            LangChain + OpenAI yanıt üretimi
├── scrapers/                 Web sitesi tarayıcısı
├── templates/ ve static/     Arayüz
└── requirements.txt
images/                       Çalışma kaydı (video)
```

## Kurulum

Gereksinimler: Python 3.8+ ve bir OpenAI API anahtarı.

```bash
cd kutuphane-sistem
pip install -r requirements.txt
```

Aynı klasörde bir ortam dosyası oluşturup şu değişkenleri tanımlayın (değerleri depoya eklemeyin): `OPENAI_API_KEY`, kütüphane servis adresi ve kullanıcı bilgileri, Yordam erişim anahtarı. Değişken adları için `integrations/` altındaki dosyalara bakın.

```bash
uvicorn app:app --reload
```

Uygulama `http://localhost:8000` adresinde açılır.

## Notlar

- Kütüphane servis adresleri ve web sitesi yapısı Batman Üniversitesi'ne özeldir; başka bir kurum için uyarlanması gerekir.
- Yordam servisine erişilemezse örnek (mock) veri yedeği kodda bulunur.
