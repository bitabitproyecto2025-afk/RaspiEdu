from pathlib import Path
from fastapi import FastAPI
from fastapi import Request, Response
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app import models
from app.seed import ensure_admin
from app.routers import users, classes, content  # agrega otros routers si existen

app = FastAPI(title="RaspiEdu API", docs_url="/docs", redoc_url=None)

@app.api_route("/ui", methods=["GET","HEAD"], include_in_schema=False)
def ui_entry(req: Request):
    if req.method == "HEAD":
        return Response(status_code=200)
    return RedirectResponse("/static/ui/index.html", status_code=302)

app.mount("/content/files", StaticFiles(directory="/data/content"), name="content_files")

# Static dir absoluto
STATIC_DIR = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.on_event("startup")
def on_startup():
    models.init_db()
    ensure_admin()

@app.get("/health")
def health():
    return {"ok": True}

# Landing sin auth
@app.get("/", include_in_schema=False)
def landing():
    return RedirectResponse(url="/static/site/index.html")

# Routers (sin prefix interno en cada archivo)
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(classes.router, prefix="/classes", tags=["classes"])
app.include_router(content.router, prefix="/content", tags=["content"])
