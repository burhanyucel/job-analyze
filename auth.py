from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import os

SECRET_KEY = os.getenv("SECRET_KEY", "gizli-anahtar-123")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def sifreyi_hashle(sifre: str):
    return pwd_context.hash(sifre)

def sifreyi_dogrula(sifre: str, hash: str):
    return pwd_context.verify(sifre, hash)

def token_olustur(data: dict):
    kopya = data.copy()
    bitis = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    kopya.update({"exp": bitis})
    return jwt.encode(kopya, SECRET_KEY, algorithm=ALGORITHM)

def tokeni_coz(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None