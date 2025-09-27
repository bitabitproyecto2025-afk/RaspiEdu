from pathlib import Path
from typing import Optional, List, Dict
from urllib.parse import quote
from fastapi import APIRouter
from fastapi.responses import RedirectResponse
import json, os

router = APIRouter()

CONTENT_ROOT = Path(os.getenv("CONTENT_ROOT", "/data/content"))
GRADES_ROOT = CONTENT_ROOT / "grades"          # /data/content/grades/<1..7>/{pdf,videos,html5,audio}
SITE_ROOT = Path(__file__).resolve().parents[1] / "static" / "site"
RES_JSON = SITE_ROOT / "resources.json"        # opcional

AUDIO_EXT = {".mp3", ".ogg", ".wav", ".m4a", ".aac"}
VIDEO_EXT = {".mp4", ".webm", ".ogg"}

def scan_grade(grado: int) -> List[Dict]:
    out: List[Dict] = []
    gdir = GRADES_ROOT / str(grado)
    if not gdir.exists():
        return out

    # PDFs
    pdf_dir = gdir / "pdf"
    if pdf_dir.exists():
        for p in pdf_dir.glob("**/*.pdf"):
            url = "/content/files/" + p.relative_to(CONTENT_ROOT).as_posix()
            out.append({"grado": grado, "tipo": "pdf", "titulo": p.stem, "url": quote(url, safe="/:")})

    # Audio
    a_dir = gdir / "audio"
    if a_dir.exists():
        for p in a_dir.glob("**/*"):
            if p.is_file() and p.suffix.lower() in AUDIO_EXT:
                url = "/content/files/" + p.relative_to(CONTENT_ROOT).as_posix()
                out.append({"grado": grado, "tipo": "audio", "titulo": p.stem, "url": quote(url, safe="/:")})

    # Videos
    v_dir = gdir / "videos"
    if v_dir.exists():
        for p in v_dir.glob("**/*"):
            if p.is_file() and p.suffix.lower() in VIDEO_EXT:
                url = "/content/files/" + p.relative_to(CONTENT_ROOT).as_posix()
                out.append({"grado": grado, "tipo": "video", "titulo": p.stem, "url": quote(url, safe="/:")})

    # HTML5
    h_dir = gdir / "html5"
    if h_dir.exists():
        for pkg in [d for d in h_dir.iterdir() if d.is_dir()]:
            index = None
            for cand in ("index.html", "Index.html", "inicio.html", "start.html"):
                if (pkg / cand).exists():
                    index = pkg / cand; break
            if not index:
                htmls = list(pkg.glob("*.html"))
                if htmls: index = htmls[0]
            if index:
                url = "/content/files/" + index.relative_to(CONTENT_ROOT).as_posix()
                out.append({"grado": grado, "tipo": "html5", "titulo": pkg.name, "url": quote(url, safe="/:")})
    return out

def items_from_json(grado: Optional[int]) -> List[Dict]:
    if not RES_JSON.exists():
        return []
    try:
        raw = json.loads(RES_JSON.read_text(encoding="utf-8"))
        items = raw.get("items", raw if isinstance(raw, list) else [])
        if grado is not None:
            items = [x for x in items if str(x.get("grado")) == str(grado)]
        return items
    except Exception:
        return []

@router.get("", include_in_schema=False)
def content_root():
    return RedirectResponse(url="/static/site/contenido.html")

@router.get("/api")
def content_api(grado: Optional[int] = None):
    scanned: List[Dict] = []
    if grado is not None:
        scanned = scan_grade(grado)
    else:
        for g in range(1, 8):
            scanned.extend(scan_grade(g))

    declared = items_from_json(grado)

    seen, merged = set(), []
    for it in declared + scanned:
        url = it.get("url")
        if not url or url in seen: continue
        seen.add(url); merged.append(it)
    return {"items": merged}
