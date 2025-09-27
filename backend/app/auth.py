from datetime import datetime, timedelta
from passlib.hash import bcrypt
import os

SECRET = os.getenv("JWT_SECRET", "change-me")
ALGO = "HS256"
EXPIRE_MIN = int(os.getenv("JWT_EXPIRE_MIN", "120"))

def hash_password(p):
    return bcrypt.hash(p)

def verify_password(p, h):
    return bcrypt.verify(p, h)

def create_token(sub: str):
    exp = datetime.utcnow() + timedelta(minutes=EXPIRE_MIN)
    return jwt.encode({"sub": sub, "exp": exp}, SECRET, algorithm=ALGO)
