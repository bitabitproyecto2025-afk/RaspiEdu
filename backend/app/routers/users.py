from fastapi import APIRouter, Depends, HTTPException, Body
from sqlmodel import Session
from app.deps import get_session
from app.models import User
from app.auth import verify_password, create_token, hash_password


router = APIRouter()


@router.post("/login")
def login(email: str = Body(...), password: str = Body(...), session: Session = Depends(get_session)):
u = session.query(User).filter(User.email == email).first()
if not u or not verify_password(password, u.password_hash):
raise HTTPException(status_code=401, detail="Credenciales inválidas")
return {"access_token": create_token(u.email)}


@router.post("/create")
def create_user(nombres: str, apellidos: str, email: str, role: str, password: str, session: Session = Depends(get_session)):
if session.query(User).filter(User.email == email).first():
raise HTTPException(status_code=400, detail="Email ya existe")
u = User(nombres=nombres, apellidos=apellidos, email=email, role=role, password_hash=hash_password(password))
session.add(u)
session.commit()
return {"id": u.id}
