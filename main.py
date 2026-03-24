from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import google.generativeai as genai
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from database import SessionLocal, veritabani_olustur, Analiz
import os

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash-lite")

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

veritabani_olustur()

class IlanModel(BaseModel):
    baslik: str
    sirket: str
    aciklama: str = ""

def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def ana_sayfa():
    return {"mesaj": "Merhaba, ilk API'n calisiyor!"}

@app.post("/ilan-analiz")
def ilan_analiz(ilan: IlanModel, db: Session = Depends(db_session)):
    if not ilan.baslik.strip():
        return {"hata": "Baslik bos olamaz"}
    if not ilan.sirket.strip():
        return {"hata": "Sirket bos olamaz"}

    mesaj = f"""
    Su is ilanini analiz et:
    Baslik: {ilan.baslik}
    Sirket: {ilan.sirket}
    Aciklama: {ilan.aciklama}
    
    Kurallar:
    - Cevabi Turkce ver
    - Kisa ve net yaz
    - Gereksiz giris cumlesi yazma
    - Sadece asagidaki 3 basligi kullan
    - Her baslik altinda madde madde yaz

    Basliklar:
    1. Gerekli beceriler
    2. Junior developer icin eksik olabilecek beceriler
    3. CV icin 3 oneri
    """

    try:
        response = model.generate_content(mesaj)
        sonuc = response.text

        analiz = Analiz(
            baslik=ilan.baslik,
            sirket=ilan.sirket,
            aciklama=ilan.aciklama,
            sonuc=sonuc
        )
        db.add(analiz)
        db.commit()

        return {
            "baslik": ilan.baslik,
            "sirket": ilan.sirket,
            "analiz": sonuc
        }

    except Exception as e:
        return {
            "baslik": ilan.baslik,
            "sirket": ilan.sirket,
            "hata": str(e)
        }

@app.get("/gecmis")
def gecmis_analizler(db: Session = Depends(db_session)):
    analizler = db.query(Analiz).order_by(Analiz.tarih.desc()).all()
    return [
        {
            "id": a.id,
            "baslik": a.baslik,
            "sirket": a.sirket,
            "tarih": a.tarih,
            "sonuc": a.sonuc
        }
        for a in analizler
    ]