from typing import Optional
from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session
from app.models import get_session

# Sesión SQLAlchemy
def get_session_dep() -> Session:
    return get_session()

# Auth mínima: acepta "Authorization: Bearer ok"
def get_current_user(authorization: Optional[str] = Header(None), db: Session = Depends(get_session_dep)):
    if not authorization:
        raise HTTPException(401, "No auth")
    parts = authorization.split()
    token = parts[-1] if parts else ""
    if token != "ok":
        raise HTTPException(401, "Token inválido")
    # Retorna un "usuario" mínimo para dependencias
    return {"role": "admin"}
