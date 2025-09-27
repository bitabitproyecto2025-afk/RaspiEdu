from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app import models

router = APIRouter()  # sin prefix; main.py añade /classes

class EnrollIn(BaseModel):
    user_id: int

def S() -> Session: return models.get_session()

class GradeIn(BaseModel):
    grado: int
    paralelo: str
    school_year: int

class SubjectIn(BaseModel):
    nombre: str

class ClassroomIn(BaseModel):
    grade_id: int
    subject_id: int

@router.post("/grades/{grade_id}/enroll")
def enroll_student_body(grade_id: int, payload: EnrollIn, db: Session = Depends(S)):
    u = db.get(models.User, payload.user_id)
    if not u or u.role != "estudiante":
        from fastapi import HTTPException
        raise HTTPException(400, "usuario no es estudiante")
    g = db.get(models.Grade, grade_id)
    if not g:
        from fastapi import HTTPException
        raise HTTPException(404, "grado no existe")
    db.query(models.Enrollment).filter(models.Enrollment.student_id == payload.user_id).delete()
    db.add(models.Enrollment(student_id=payload.user_id, grade_id=grade_id))
    db.commit()
    return {"ok": True}

@router.get("/grades")
def list_grades(db: Session = Depends(S)):
    return db.query(models.Grade).order_by(
        models.Grade.school_year.desc(), models.Grade.grado, models.Grade.paralelo
    ).all()

@router.post("/grades")
def create_grade(payload: GradeIn, db: Session = Depends(S)):
    g = models.Grade(**payload.model_dump())
    db.add(g); db.commit(); db.refresh(g)
    return g

@router.delete("/grades/{grade_id}")
def delete_grade(grade_id: int, db: Session = Depends(S)):
    g = db.get(models.Grade, grade_id)
    if not g: raise HTTPException(404, "no existe")
    db.delete(g); db.commit()
    return {"ok": True}

@router.get("/subjects")
def list_subjects(db: Session = Depends(S)):
    return db.query(models.Subject).order_by(models.Subject.nombre).all()

@router.post("/subjects")
def create_subject(payload: SubjectIn, db: Session = Depends(S)):
    s = models.Subject(**payload.model_dump())
    db.add(s); db.commit(); db.refresh(s)
    return s

@router.delete("/subjects/{subject_id}")
def delete_subject(subject_id: int, db: Session = Depends(S)):
    s = db.get(models.Subject, subject_id)
    if not s: raise HTTPException(404, "no existe")
    db.delete(s); db.commit()
    return {"ok": True}

@router.get("/classrooms")
def list_classrooms(db: Session = Depends(S)):
    return db.query(models.Classroom).all()

@router.post("/classrooms")
def create_classroom(payload: ClassroomIn, db: Session = Depends(S)):
    c = models.Classroom(**payload.model_dump())
    db.add(c); db.commit(); db.refresh(c)
    return c

@router.delete("/classrooms/{classroom_id}")
def delete_classroom(classroom_id: int, db: Session = Depends(S)):
    c = db.get(models.Classroom, classroom_id)
    if not c: raise HTTPException(404, "no existe")
    db.delete(c); db.commit()
    return {"ok": True}

@router.post("/grades/{grade_id}/enroll/{user_id}")
def enroll_student(grade_id: int, user_id: int, db: Session = Depends(S)):
    u = db.get(models.User, user_id)
    if not u or u.role != "estudiante": raise HTTPException(400, "usuario no es estudiante")
    g = db.get(models.Grade, grade_id)
    if not g: raise HTTPException(404, "grado no existe")
    db.query(models.Enrollment).filter(models.Enrollment.student_id == user_id).delete()
    db.add(models.Enrollment(student_id=user_id, grade_id=grade_id)); db.commit()
    return {"ok": True}

@router.delete("/grades/{grade_id}/enroll/{user_id}")
def unenroll_student(grade_id: int, user_id: int, db: Session = Depends(S)):
    db.query(models.Enrollment).filter(
        models.Enrollment.grade_id == grade_id,
        models.Enrollment.student_id == user_id
    ).delete()
    db.commit()
    return {"ok": True}

@router.post("/classrooms/{classroom_id}/teachers/{user_id}")
def add_teacher(classroom_id: int, user_id: int, db: Session = Depends(S)):
    c = db.get(models.Classroom, classroom_id); u = db.get(models.User, user_id)
    if not c or not u: raise HTTPException(404, "no existe")
    if u.role not in ("docente", "admin"): raise HTTPException(400, "no docente")
    if u not in c.teachers: c.teachers.append(u); db.commit()
    return {"ok": True}

@router.delete("/classrooms/{classroom_id}/teachers/{user_id}")
def remove_teacher(classroom_id: int, user_id: int, db: Session = Depends(S)):
    c = db.get(models.Classroom, classroom_id); u = db.get(models.User, user_id)
    if not c or not u: raise HTTPException(404, "no existe")
    if u in c.teachers: c.teachers.remove(u); db.commit()
    return {"ok": True}

@router.get("/grades/{grade_id}/detail")
def grade_detail(grade_id: int, db: Session = Depends(S)):
    g = db.get(models.Grade, grade_id)
    if not g: raise HTTPException(404, "no existe")
    subs = db.query(models.Subject).all()
    subj_map = {s.id: s.nombre for s in subs}
    classrooms = db.query(models.Classroom).filter_by(grade_id=grade_id).all()
    cls = [{
        "id": c.id,
        "subject": subj_map.get(c.subject_id, ""),
        "teachers": [{"id": t.id, "nombre": f"{t.nombres} {t.apellidos}", "email": t.email} for t in c.teachers],
    } for c in classrooms]
    students = db.query(models.Enrollment).filter_by(grade_id=grade_id).all()
    st = []
    for e in students:
        u = db.get(models.User, e.student_id)
        if u: st.append({"id": u.id, "nombre": f"{u.nombres} {u.apellidos}", "email": u.email})
    return {"id": g.id, "grado": g.grado, "paralelo": g.paralelo, "school_year": g.school_year,
            "classrooms": cls, "students": st}
