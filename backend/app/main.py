from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader, select_autoescape
from app import models
from app.deps import get_session, get_current_user
from sqlmodel import SQLModel, Session
from app.seed import ensure_admin
from app.routers import users, classes, content


app = FastAPI(title="RaspiEdu")
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(classes.router, prefix="/classes", tags=["classes"])
app.include_router(content.router, prefix="/content", tags=["content"])
app.mount("/static", StaticFiles(directory="app/static"), name="static")


templates = Environment(
loader=FileSystemLoader("app/templates"),
autoescape=select_autoescape()
)


@app.on_event("startup")
def on_startup():
models.init_db()
ensure_admin()


@app.get("/", response_class=HTMLResponse)
async def root(request: Request, user=Depends(get_current_user)):
# Redirige al tablero según rol.
if user.role == "admin":
return RedirectResponse("/content/admin")
if user.role == "docente":
return RedirectResponse("/content/docente")
return RedirectResponse("/content/estudiante")
