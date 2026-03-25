from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

SQLALCHEMY_DATABASE_URL = "sqlite:///./analizler.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Kullanici(Base):
    __tablename__ = "kullanicilar"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    sifre_hash = Column(String, nullable=False)
    tarih = Column(DateTime, default=datetime.utcnow)
    analizler = relationship("Analiz", back_populates="kullanici")

class Analiz(Base):
    __tablename__ = "analizler"

    id = Column(Integer, primary_key=True, index=True)
    kullanici_id = Column(Integer, ForeignKey("kullanicilar.id"))
    baslik = Column(String, nullable=False)
    sirket = Column(String, nullable=False)
    aciklama = Column(Text, default="")
    sonuc = Column(Text, nullable=False)
    tarih = Column(DateTime, default=datetime.utcnow)
    kullanici = relationship("Kullanici", back_populates="analizler")

def veritabani_olustur():
    Base.metadata.create_all(bind=engine)