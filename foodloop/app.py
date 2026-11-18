"""FoodLoop review app (prototype). Run: uvicorn foodloop.app:app"""
import io
import os
import secrets
import uuid
from pathlib import Path

from fastapi import Depends, FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.templating import Jinja2Templates
from PIL import Image

from . import classifier
from .ledger import Ledger, LedgerError
from .router import ROUTES, ROUTE_LABELS, propose_route

BASE = Path(__file__).resolve().parent
DATA = Path(os.environ.get("FOODLOOP_DATA", BASE.parent / "data"))
UPLOADS = DATA / "uploads"
UPLOADS.mkdir(parents=True, exist_ok=True)
MAX_BYTES = 5 * 1024 * 1024
CATEGORIES = {"produce": False, "grain_or_bakery": False,
              "meat": True, "dairy": True, "ready_to_eat": True}

ledger = Ledger(str(DATA / "foodloop.db"))
templates = Jinja2Templates(directory=str(BASE / "templates"))
security = HTTPBasic(auto_error=False)


def require_login(creds: HTTPBasicCredentials | None = Depends(security)):
    """Optional login. Set FOODLOOP_USER and FOODLOOP_PASSWORD to turn it on."""
    user, pw = os.environ.get("FOODLOOP_USER"), os.environ.get("FOODLOOP_PASSWORD")
    if not user or not pw:
        return
    ok = creds and secrets.compare_digest(creds.username, user) and secrets.compare_digest(creds.password, pw)
    if not ok:
        raise HTTPException(401, "Login required", headers={"WWW-Authenticate": "Basic"})


app = FastAPI(title="FoodLoop prototype", dependencies=[Depends(require_login)])


def _ctx(**kw):
    return {"routes": ROUTES, "route_labels": ROUTE_LABELS, **kw}


@app.get("/")
def index(request: Request):
    return templates.TemplateResponse(request, "index.html", _ctx(categories=list(CATEGORIES)))


@app.post("/scan")
async def scan(request: Request, photo: UploadFile = File(...), category: str = Form("produce"),
               source: str = Form("")):
    if category not in CATEGORIES:
        raise HTTPException(400, "Unknown category")
    data = await photo.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise HTTPException(413, "Photo is larger than 5 MB")
    try:
        img = Image.open(io.BytesIO(data))
        img.verify()
        pred = classifier.predict(data)
    except Exception:
        raise HTTPException(400, "Could not read that as an image")
    higher_risk = CATEGORIES[category]
    decision = propose_route(pred["label"], pred["confidence"], higher_risk)
    batch_id = uuid.uuid4().hex[:10]
    (UPLOADS / f"{batch_id}.jpg").write_bytes(_to_jpeg(data))
    ledger.propose(batch_id, {**pred, "category": category, "higher_risk": higher_risk,
                              "source": source.strip()[:80], "proposed_route": decision.route,
                              "reason": decision.reason})
    return RedirectResponse(f"/batch/{batch_id}", status_code=303)


def _to_jpeg(data: bytes) -> bytes:
    img = Image.open(io.BytesIO(data)).convert("RGB")
    img.thumbnail((1024, 1024))
    out = io.BytesIO()
    img.save(out, "JPEG", quality=85)
    return out.getvalue()


def _batch_or_404(batch_id: str):
    events = ledger.events(batch_id)
    if not events:
        raise HTTPException(404, "Batch not found")
    proposal = events[0]["payload"]
    return events, proposal, ledger.state(batch_id)


@app.get("/batch/{batch_id}")
def batch(request: Request, batch_id: str, error: str = ""):
    events, proposal, state = _batch_or_404(batch_id)
    return templates.TemplateResponse(request, "batch.html", _ctx(
        batch_id=batch_id, events=events, p=proposal, s=state, error=error))


@app.get("/image/{batch_id}")
def image(batch_id: str):
    if not batch_id.isalnum():
        raise HTTPException(404)
    path = UPLOADS / f"{batch_id}.jpg"
    if not path.exists():
        raise HTTPException(404)
    return FileResponse(path, media_type="image/jpeg")


def _act(batch_id: str, fn):
    try:
        fn()
    except LedgerError as e:
        return RedirectResponse(f"/batch/{batch_id}?error={e}", status_code=303)
    return RedirectResponse(f"/batch/{batch_id}", status_code=303)


@app.post("/batch/{batch_id}/review")
def review(batch_id: str, reviewer: str = Form(""), final_route: str = Form(...)):
    _, proposal, _ = _batch_or_404(batch_id)
    if final_route not in ROUTES:
        raise HTTPException(400, "Unknown route")
    return _act(batch_id, lambda: ledger.review(batch_id, reviewer, final_route, proposal["proposed_route"]))


@app.post("/batch/{batch_id}/confirm/{role}")
def confirm(batch_id: str, role: str, name: str = Form("")):
    _batch_or_404(batch_id)
    return _act(batch_id, lambda: ledger.confirm(batch_id, role, name))


@app.get("/batches")
def batches(request: Request):
    rows = []
    for e in ledger.all_entries():
        if e["event"] == "scan_proposed":
            rows.append({"id": e["batch_id"], "ts": e["ts"], "p": e["payload"],
                         "s": ledger.state(e["batch_id"])})
    return templates.TemplateResponse(request, "batches.html", _ctx(rows=list(reversed(rows))))


@app.get("/ledger")
def ledger_page(request: Request):
    ok, msg = ledger.verify()
    return templates.TemplateResponse(request, "ledger.html", _ctx(
        entries=list(reversed(ledger.all_entries())), ok=ok, msg=msg))


@app.get("/health")
def health():
    return {"status": "ok"}
