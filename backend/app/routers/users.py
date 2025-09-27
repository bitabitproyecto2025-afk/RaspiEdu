from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from typing import Optional
from app.models import User, get_session

router = APIRouter()

# hash helpers
try:
    from passlib.hash import pbkdf2_sha256
    def hash_pw(p: str) -> str: return pbkdf2_sha256.hash(p)
    def verify_pw(p: str, h: str) -> bool: return pbkdf2_sha256.verify(p, h)
except Exception:
    def hash_pw(p: str) -> str: return "plain:" + p
    def verify_pw(p: str, h: str) -> bool: return h == "plain:" + p

def S() -> Session: return get_session()

class UserCreate(BaseModel):
    nombres: str
    apellidos: str
    email: EmailStr
    role: str  # admin|docente|estudiante
    password: str

class LoginIn(BaseModel):
    email: EmailStr
    password: str

@router.post("/create")
def create_user(payload: UserCreate, db: Session = Depends(S)):
    if db.query(User).filter(User.email == payload.email.lower()).first():
        raise HTTPException(400, "email ya existe")
    u = User(
        nombres=payload.nombres.strip(),
        apellidos=payload.apellidos.strip(),
        email=payload.email.lower(),
        role=payload.role,
        password_hash=hash_pw(payload.password),
    )
    db.add(u); db.commit(); db.refresh(u)
    return {"id": u.id, "email": u.email}

@router.post("/login")
def login(payload: LoginIn, db: Session = Depends(S)):
    u = db.query(User).filter(User.email == payload.email.lower()).first()
    if not u or not verify_pw(payload.password, u.password_hash):
        raise HTTPException(401, "credenciales inválidas")
    return {"access_token": "ok", "token_type": "bearer", "user": {"id": u.id, "role": u.role}}

@router.get("")
def list_users(role: Optional[str] = None, db: Session = Depends(S)):
    q = db.query(User)
    if role: q = q.filter(User.role == role)
    return q.order_by(User.apellidos, User.nombres).all()

@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(S)):
    u = db.get(User, user_id)
    if not u: raise HTTPException(404, "no existe")
    db.delete(u); db.commit()
    return {"ok": True}
