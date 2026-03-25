from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from google import genai
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from database import SessionLocal, veritabani_olustur, Analiz, Kullanici
from auth import sifreyi_hashle, sifreyi_dogrula, token_olustur, tokeni_coz
import os

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

veritabani_olustur()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="giris")

class IlanModel(BaseModel):
    baslik: str
    sirket: str
    aciklama: str = ""

class KullaniciKayit(BaseModel):
    email: str
    sifre: str

def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def aktif_kullanici(token: str = Depends(oauth2_scheme), db: Session = Depends(db_session)):
    email = tokeni_coz(token)
    if not email:
        raise HTTPException(status_code=401, detail="Gecersiz token")
    kullanici = db.query(Kullanici).filter(Kullanici.email == email).first()
    if not kullanici:
        raise HTTPException(status_code=401, detail="Kullanici bulunamadi")
    return kullanici

@app.get("/")
def ana_sayfa():
    return {"mesaj": "Merhaba, ilk API'n calisiyor!"}

@app.post("/kayit")
def kayit(veri: KullaniciKayit, db: Session = Depends(db_session)):
    mevcut = db.query(Kullanici).filter(Kullanici.email == veri.email).first()
    if mevcut:
        raise HTTPException(status_code=400, detail="Bu email zaten kayitli")
    kullanici = Kullanici(
        email=veri.email,
        sifre_hash=sifreyi_hashle(veri.sifre)
    )
    db.add(kullanici)
    db.commit()
    return {"mesaj": "Kayit basarili"}

@app.post("/giris")
def giris(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(db_session)):
    kullanici = db.query(Kullanici).filter(Kullanici.email == form.username).first()
    if not kullanici or not sifreyi_dogrula(form.password, kullanici.sifre_hash):
        raise HTTPException(status_code=401, detail="Email veya sifre yanlis")
    token = token_olustur({"sub": kullanici.email})
    return {"access_token": token, "token_type": "bearer"}

@app.post("/ilan-analiz")
def ilan_analiz(ilan: IlanModel, kullanici: Kullanici = Depends(aktif_kullanici), db: Session = Depends(db_session)):
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
        response = client.models.generate_content(model="gemini-2.5-flash-lite", contents=mesaj)
        sonuc = response.text

        analiz = Analiz(
            kullanici_id=kullanici.id,
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
        return {"hata": str(e)}

@app.get("/gecmis")
def gecmis_analizler(kullanici: Kullanici = Depends(aktif_kullanici), db: Session = Depends(db_session)):
    analizler = db.query(Analiz).filter(
        Analiz.kullanici_id == kullanici.id
    ).order_by(Analiz.tarih.desc()).all()
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