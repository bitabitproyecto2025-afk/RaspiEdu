from typing import Optional
from sqlmodel import SQLModel, Field, create_engine
import os


DB_URL = os.getenv("DB_URL", "sqlite:////data/app.db")
engine = create_engine(DB_URL, connect_args={"check_same_thread": False})


class User(SQLModel, table=True):
id: Optional[int] = Field(default=None, primary_key=True)
nombres: str
apellidos: str
email: str
password_hash: str
role: str # admin|docente|estudiante


class Grade(SQLModel, table=True):
id: Optional[int] = Field(default=None, primary_key=True)
grado: int # 1..7
paralelo: str # A..N


class Subject(SQLModel, table=True):
id: Optional[int] = Field(default=None, primary_key=True)
nombre: str # Matemática, Lengua, etc.


class Classroom(SQLModel, table=True):
id: Optional[int] = Field(default=None, primary_key=True)
grade_id: int
subject_id: int


class Enrollment(SQLModel, table=True):
id: Optional[int] = Field(default=None, primary_key=True)
user_id: int
classroom_id: int


class ContentItem(SQLModel, table=True):
id: Optional[int] = Field(default=None, primary_key=True)
classroom_id: Optional[int] = None # None = global
tipo: str # link|archivo|phet|kiwix|kolibri
titulo: str
descripcion: str = ""
path: str # ruta local o URL relativa


def init_db():
SQLModel.metadata.create_all(engine)
