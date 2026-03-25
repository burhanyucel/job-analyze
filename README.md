# İş İlanı Analiz Aracı

AI destekli iş ilanı analiz uygulaması. İş ilanını yapıştır, Gemini AI gerekli becerileri ve CV önerilerini analiz etsin.

## 🚀 Canlı Demo
https://job-analyze.onrender.com/static/index.html

## 🛠 Teknolojiler
- Python + FastAPI
- Google Gemini AI
- SQLite + SQLAlchemy
- JWT Authentication
- HTML/CSS/JavaScript

## ⚙️ Özellikler
- Kullanıcı kayıt ve giriş sistemi
- JWT token ile güvenli API
- Her kullanıcı sadece kendi analizlerini görür
- Geçmiş analizler kaydedilir

## 🔧 Kurulum
1. Repoyu klonla
2. `pip install -r requirements.txt`
3. `.env` dosyası oluştur: `GEMINI_API_KEY=your_key`
4. `uvicorn main:app --reload`
