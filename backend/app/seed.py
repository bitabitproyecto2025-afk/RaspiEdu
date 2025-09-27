import os
from sqlalchemy import text
from app.models import get_session
try:
    from passlib.hash import pbkdf2_sha256
    def hash_pw(p: str) -> str: return pbkdf2_sha256.hash(p)
except Exception:
    def hash_pw(p: str) -> str: return "plain:" + p

def ensure_admin():
    email = os.getenv("ADMIN_EMAIL","admin@escuela.local").lower()
    password = os.getenv("ADMIN_PASSWORD","BitaBit2025##!")
    nombres = os.getenv("ADMIN_FIRSTNAME","Admin")
    apellidos = os.getenv("ADMIN_LASTNAME","Escuela")
    with get_session() as db:
        db.execute(text("""
            INSERT OR IGNORE INTO users (nombres, apellidos, email, role, password_hash)
            VALUES (:n,:a,:e,'admin',:p)
        """), {"n":nombres,"a":apellidos,"e":email,"p":hash_pw(password)})
        db.commit()
