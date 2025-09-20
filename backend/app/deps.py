from fastapi import Depends, HTTPException, Header
from jose import jwt, JWTError
from sqlmodel import Session
from app.models import engine, User
import os


SECRET = os.getenv("JWT_SECRET", "change-me")
ALGO = "HS256"


def get_session():
with Session(engine) as s:
yield s


def get_current_user(authorization: str | None = Header(default=None), session: Session = Depends(get_session)):
if not authorization or not authorization.startswith("Bearer "):
raise HTTPException(status_code=401, detail="No auth")
token = authorization.split()[1]
try:
payload = jwt.decode(token, SECRET, algorithms=[ALGO])
email = payload.get("sub")
user = session.query(User).filter(User.email == email).first()
if not user:
raise HTTPException(status_code=401, detail="User not found")
return user
except JWTError:
raise HTTPException(status_code=401, detail="Invalid token")
