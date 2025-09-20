from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.deps import get_session
from app.models import Grade, Subject, Classroom


router = APIRouter()


# ----- Grade -----
@router.post("/grades")
def create_grade(grado: int, paralelo: str, session: Session = Depends(get_session)):
exists = session.exec(select(Grade).where(Grade.grado==grado, Grade.paralelo==paralelo)).first()
if exists:
raise HTTPException(status_code=400, detail="Grado+paralelo ya existe")
g = Grade(grado=grado, paralelo=paralelo)
session.add(g); session.commit(); session.refresh(g)
return g


@router.get("/grades")
def list_grades(session: Session = Depends(get_session)):
return session.exec(select(Grade).order_by(Grade.grado, Grade.paralelo)).all()


@router.delete("/grades/{gid}")
def delete_grade(gid: int, session: Session = Depends(get_session)):
g = session.get(Grade, gid)
if not g:
raise HTTPException(status_code=404, detail="No encontrado")
session.delete(g); session.commit(); return {"ok": True}


# ----- Subject -----
@router.post("/subjects")
def create_subject(nombre: str, session: Session = Depends(get_session)):
exists = session.exec(select(Subject).where(Subject.nombre==nombre)).first()
if exists:
raise HTTPException(status_code=400, detail="Materia ya existe")
s = Subject(nombre=nombre)
session.add(s); session.commit(); session.refresh(s)
return s


@router.get("/subjects")
def list_subjects(session: Session = Depends(get_session)):
return session.exec(select(Subject).order_by(Subject.nombre)).all()


@router.delete("/subjects/{sid}")
def delete_subject(sid: int, session: Session = Depends(get_session)):
s = session.get(Subject, sid)
if not s:
raise HTTPException(status_code=404, detail="No encontrado")
session.delete(s); session.commit(); return {"ok": True}


# ----- Classroom -----
@router.post("/classrooms")
def create_classroom(grade_id: int, subject_id: int, session: Session = Depends(get_session)):
exists = session.exec(select(Classroom).where(Classroom.grade_id==grade_id, Classroom.subject_id==subject_id)).first()
if exists:
raise HTTPException(status_code=400, detail="Aula ya existe para ese grado+materia")
c = Classroom(grade_id=grade_id, subject_id=subject_id)
session.add(c); session.commit(); session.refresh(c)
return c


@router.get("/classrooms")
def list_classrooms(session: Session = Depends(get_session)):
return session.exec(select(Classroom)).all()


@router.delete("/classrooms/{cid}")
def delete_classroom(cid: int, session: Session = Depends(get_session)):
c = session.get(Classroom, cid)
if not c:
raise HTTPException(status_code=404, detail="No encontrado")
session.delete(c); session.commit(); return {"ok": True}
