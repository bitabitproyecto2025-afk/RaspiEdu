from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.deps import get_session
from app.models import ContentItem


router = APIRouter()


@router.post("")
def create_content(tipo: str, titulo: str, path: str, descripcion: str = "", classroom_id: int | None = None, session: Session = Depends(get_session)):
c = ContentItem(tipo=tipo, titulo=titulo, path=path, descripcion=descripcion, classroom_id=classroom_id)
session.add(c); session.commit(); session.refresh(c)
return c


@router.get("")
def list_content(classroom_id: int | None = None, session: Session = Depends(get_session)):
q = select(ContentItem)
if classroom_id is not None:
q = q.where(ContentItem.classroom_id == classroom_id)
return session.exec(q).all()


@router.get("/{cid}")
def get_content(cid: int, session: Session = Depends(get_session)):
c = session.get(ContentItem, cid)
if not c:
raise HTTPException(status_code=404, detail="No encontrado")
return c


@router.delete("/{cid}")
def delete_content(cid: int, session: Session = Depends(get_session)):
c = session.get(ContentItem, cid)
if not c:
raise HTTPException(status_code=404, detail="No encontrado")
session.delete(c); session.commit(); return {"ok": True}
