from datetime import datetime
from typing import List, Optional
import os

from sqlalchemy import (
    create_engine, Integer, String, ForeignKey, Table, Column, UniqueConstraint
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session
from sqlalchemy.pool import NullPool

# SQLite sin pooling para evitar timeouts/bloqueos con uvicorn
DB_URL = os.getenv("DB_URL", "sqlite:////data/app.db")
engine = create_engine(
    DB_URL,
    connect_args={"check_same_thread": False, "timeout": 30},
    poolclass=NullPool,   # clave para eliminar QueuePool
    future=True,
)

class Base(DeclarativeBase):
    pass

# --- Usuarios ---
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombres: Mapped[str] = mapped_column(String(120))
    apellidos: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(160), unique=True)
    role: Mapped[str] = mapped_column(String(20))  # admin|docente|estudiante
    password_hash: Mapped[str] = mapped_column(String(200))

    classrooms: Mapped[List["Classroom"]] = relationship(
        secondary="teacher_classrooms", back_populates="teachers"
    )
    enrollment: Mapped[Optional["Enrollment"]] = relationship(
        back_populates="student", uselist=False
    )

# --- Catálogo ---
class Grade(Base):
    __tablename__ = "grades"
    id: Mapped[int] = mapped_column(primary_key=True)
    grado: Mapped[int] = mapped_column(Integer)        # 1..7
    paralelo: Mapped[str] = mapped_column(String(2))   # A..Z
    school_year: Mapped[int] = mapped_column(Integer, default=datetime.now().year)
    __table_args__ = (UniqueConstraint("grado", "paralelo", "school_year", name="uix_grade_par_year"),)

    classrooms: Mapped[List["Classroom"]] = relationship(back_populates="grade")
    students: Mapped[List["Enrollment"]] = relationship(back_populates="grade")

class Subject(Base):
    __tablename__ = "subjects"
    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(120), unique=True)

class Classroom(Base):
    __tablename__ = "classrooms"
    id: Mapped[int] = mapped_column(primary_key=True)
    grade_id: Mapped[int] = mapped_column(ForeignKey("grades.id", ondelete="CASCADE"))
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id", ondelete="CASCADE"))
    __table_args__ = (UniqueConstraint("grade_id", "subject_id", name="uix_grade_subject"),)

    grade: Mapped["Grade"] = relationship(back_populates="classrooms")
    subject: Mapped["Subject"] = relationship()
    teachers: Mapped[List["User"]] = relationship(
        secondary="teacher_classrooms", back_populates="classrooms"
    )

# Asociación N:M docentes↔aulas (usa Column, no mapped_column)
teacher_classrooms = Table(
    "teacher_classrooms", Base.metadata,
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("classroom_id", ForeignKey("classrooms.id", ondelete="CASCADE"), primary_key=True),
    UniqueConstraint("user_id", "classroom_id", name="uix_teacher_classroom")
)

# Matrícula 1:1 estudiante→grado
class Enrollment(Base):
    __tablename__ = "enrollments"
    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    grade_id: Mapped[int] = mapped_column(ForeignKey("grades.id", ondelete="CASCADE"))
    student: Mapped["User"] = relationship(back_populates="enrollment")
    grade: Mapped["Grade"] = relationship(back_populates="students")

def init_db():
    Base.metadata.create_all(bind=engine)

def get_session():
    return Session(engine)
