from fastapi import APIRouter, HTTPException
from pathlib import Path

r = APIRouter(prefix="/content", tags=["content-auto"])

BASE = Path("app/static/grades")

def list_files(p: Path, exts):
    out = []
    if not p.exists(): return out
    for f in sorted(p.iterdir()):
        if f.is_file() and f.suffix.lower() in exts:
            out.append({
                "title": f.stem,
                "name": f.name,  # <-- nombre completo
                "href": f"/static/grades/{p.relative_to(BASE)}/{f.name}",
            })
    return out

def list_html5(p: Path):
    out = []
    if not p.exists(): return out
    for d in sorted(p.iterdir()):
        if d.is_dir() and (d / "index.html").exists():
            rel = d.relative_to(BASE)
            out.append({
                "title": d.name,
                "name": f"{d.name}/index.html",
                "href": f"/static/grades/{rel}/index.html",
            })
    return out

@r.get("/api")
def content_api(grado: int):
    if grado < 1 or grado > 7:
        raise HTTPException(400, "grado inválido")
    g = BASE / str(grado)
    return {
        "grado": grado,
        "videos": list_files(g / "videos", {".mp4", ".webm"}),
        "pdfs":   list_files(g / "pdf", {".pdf"}),
        "html5":  list_html5(g / "html5"),
    }
