from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from app.routers import users, classes, content
from app import models
from app.seed import ensure_admin
from app.deps import get_current_user

app = FastAPI(title="RaspiEdu")

app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(classes.router, prefix="/classes", tags=["classes"])
app.include_router(content.router, prefix="/content", tags=["content"])

app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/", include_in_schema=False)
def landing_get():
    p = Path("app/static/site/index.html")
    return FileResponse(p) if p.exists() else Response(status_code=404)

@app.head("/", include_in_schema=False)
def landing_head():
    return Response(status_code=200)

@app.on_event("startup")
def on_startup():
    models.init_db()
    ensure_admin()

@app.get("/", response_class=HTMLResponse)
async def root(request: Request, user=Depends(get_current_user)):
    # Redirige según rol
    if user.role == "admin":
        return RedirectResponse(url="/content/admin", status_code=302)
    if user.role == "docente":
        return RedirectResponse(url="/content/docente", status_code=302)
    return RedirectResponse(url="/content/estudiante", status_code=302)

# --- Placeholders para evitar 404 mientras no haya UI ---
@app.get("/content/admin", response_class=HTMLResponse)
async def admin_dashboard(user=Depends(get_current_user)):
    return HTMLResponse("<h1>Panel Admin</h1>")

@app.get("/content/docente", response_class=HTMLResponse)
async def docente_dashboard(user=Depends(get_current_user)):
    return HTMLResponse("<h1>Panel Docente</h1>")

@app.get("/content/estudiante", response_class=HTMLResponse)
async def estudiante_dashboard(user=Depends(get_current_user)):
    return HTMLResponse("<h1>Panel Estudiante</h1>")

@app.get("/ui", include_in_schema=False)
def ui():
    return FileResponse(Path("app/static/ui/index.html"))

@app.get("/health")
def health():
    return {"ok": True}
