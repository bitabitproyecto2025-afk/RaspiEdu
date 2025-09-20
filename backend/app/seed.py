import os
from sqlmodel import Session
from app.models import engine, User
from app.auth import hash_password


# Solo crea admin si no existe. No crea grados/materias.


def ensure_admin():
admin_email = os.getenv("ADMIN_EMAIL", "admin@local")
admin_pass = os.getenv("ADMIN_PASSWORD", "admin123")
with Session(engine) as s:
u = s.query(User).filter(User.email == admin_email).first()
if not u:
u = User(
nombres="Admin",
apellidos="Local",
email=admin_email,
password_hash=hash_password(admin_pass),
role="admin",
)
s.add(u)
s.commit()
