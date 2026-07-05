# AI CV Analiz ve Kariyer Danışmanı (Vercel Sürümü)

> **Geliştirici:** Nejdet Tut  
> **Ders:** Final Projesi — 2026  
> **Teknolojiler:** Python · FastAPI · HTML5 · CSS3 (Vanilla) · Javascript · Chart.js · Google Gemini API · Groq API · SQLite · Vercel Serverless

---

## 🚀 Özellikler

| Özellik | Açıklama |
|---|---|
| 🤖 Çift AI Modeli | Gemini (Flash/Pro) ve Groq (Llama/Mixtral) desteği |
| ⚡ FastAPI Backend | Vercel Serverless Functions uyumlu hızlı REST API |
| 🖥️ Modern Ön Uç | Emerald yeşili koyu tema, cam efekti (glassmorphism) ve responsive tasarım |
| 📊 Puan Göstergesi | Dinamik circular progress bar / gauge halkası |
| ✅ Güçlü Yönler | Yeşil kart listesi ile görsel CV analiz maddeleri |
| ❌ Eksikler | Kırmızı kart listesi ile geliştirilmesi gereken alanlar |
| 🎯 Meslek Önerileri | Yapay zekanın önerdiği meslek etiketleri (badgeler) |
| 💡 Kariyer Tavsiyeleri | Yol haritası sunan adım adım tavsiyeler |
| 📄 PDF Export | fpdf2 ile rapor oluşturma |
| 📝 Word Export | python-docx ile .docx oluşturma |
| 📊 CSV Export | Tüm geçmiş analiz verilerini tek tıkla indirme |
| 🗃️ SQLite | Analizler veritabanına kaydedilir (Lokalde kalıcı, Vercel'de geçici `/tmp` dizininde) |
| 🔍 Arama | Geçmiş analizlerde isim/alan/içerik arama |
| 📈 İstatistikler | **Chart.js** ile ön yüzde çizilen etkileşimli analitik grafikler |

---

## 📁 Dosya Yapısı

```
cv-vercel-127/
├── api/
│   └── index.py        # FastAPI API Uç Noktaları ve Yönlendirmeleri
├── database.py         # SQLite CRUD işlemleri (Vercel uyumlu dynamic DB path)
├── ai_models.py        # Gemini & Groq API entegrasyonları (Streamlit bağımsız)
├── cv_parser.py        # PDF ve URL'den metin çıkarma motoru
├── export_utils.py     # PDF, Word, CSV rapor oluşturma kütüphanesi
├── index.html          # Modern ön uç arayüz iskeleti
├── style.css           # Emerald temalı özel CSS tasarımları
├── app.js              # Ön uç etkileşim ve Chart.js grafikleri mantığı
├── vercel.json         # Vercel sunucusuz yönlendirme konfigürasyonu
├── requirements.txt    # Python bağımlılıkları (FastAPI ve Uvicorn dahil)
├── .env.example        # API anahtar şablonu
└── README.md           # Bu dosya
```

---

## ⚙️ Lokal Kurulum ve Çalıştırma

### 1. Bağımlılıkları Kur
```bash
pip install -r requirements.txt
```

### 2. API Anahtarlarını Ayarla
`.env.example` dosyasını `.env` olarak kopyalayın ve kendi API anahtarlarınızı girin:

```bash
# Windows
copy .env.example .env
# macOS/Linux
cp .env.example .env
```

`.env` dosyasını düzenleyin:
```env
GEMINI_API_KEY=AIza...gerçek_anahtarınız
GROQ_API_KEY=gsk_...gerçek_anahtarınız
```

### 3. API Sunucusunu Başlat
```bash
uvicorn api.index:app --reload
```
API sunucunuz `http://127.0.0.1:8000` adresinde çalışmaya başlayacaktır.

### 4. Ön Yüzü Açın
Projedeki `index.html` dosyasını tarayıcınızda doğrudan açarak (veya VS Code Live Server gibi bir araçla) uygulamayı kullanmaya başlayabilirsiniz.

---

## 🚀 Vercel Canlı Yayına Alma Adımları

Projeyi kendi Vercel hesabınızda yayına almak için:
1. GitHub hesabınızda bu reponun barındırıldığından emin olun.
2. [vercel.com](https://vercel.com) adresine gidin ve giriş yapın.
3. **Add New > Project** seçeneğine tıklayın.
4. GitHub listenizden bu projeyi bulun ve **Import** butonuna tıklayın.
5. Proje kurulum ekranında **Environment Variables** (Ortam Değişkenleri) alanına API anahtarlarınızı ekleyin:
   * `GEMINI_API_KEY`
   * `GROQ_API_KEY` (isteğe bağlı)
6. **Deploy** butonuna basın. Vercel, `vercel.json` yapılandırmasını okuyarak projeyi otomatik olarak canlıya alacaktır.
