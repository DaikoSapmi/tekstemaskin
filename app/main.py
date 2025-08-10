# app/main.py
from __future__ import annotations
import os
import asyncio
import json
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, Form
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .config import settings
from .transcription_worker import TranscriptionSession
from .utils import session_stamp, session_paths
from .summary_llm import summarize_to_markdown
from .offline_asr import transcribe_many_with_progress

app = FastAPI(
    title="Tekstemaskin",
    description="Real-time Speech-to-Text with Norwegian Support",
    version="1.0.0"
)
BASE_DIR = Path(__file__).resolve().parent

@app.on_event("startup")
async def startup_event():
    """Log when the application starts up"""
    print("🚀 Tekstemaskin server starting up...")
    print(f"📁 Base directory: {BASE_DIR}")
    print(f"🌐 Server will be available at: http://localhost:8000")
    print(f"🎛️  Control panel: http://localhost:8000/control")

@app.on_event("shutdown")
async def shutdown_event():
    """Log when the application shuts down"""
    print("👋 Tekstemaskin server shutting down...")

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

SESSION: Optional[TranscriptionSession] = None
# ENDRET LINJE: Bruker det korrekte navnet 'default_lang' fra config.py
LANG = settings.default_lang


class WSManager:
    def __init__(self):
        self.active: set[WebSocket] = set()
    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.add(ws)
    def disconnect(self, ws: WebSocket):
        self.active.discard(ws)
    async def broadcast_text(self, text: str):
        stale: list[WebSocket] = []
        for ws in list(self.active):
            try:
                await ws.send_text(text)
            except Exception:
                stale.append(ws)
        for ws in stale:
            self.disconnect(ws)

manager = WSManager()


@app.get("/health")
def health():
    """Health check endpoint to verify server is ready"""
    return {
        "status": "healthy", 
        "service": "tekstemaskin",
        "version": "1.0.0",
        "endpoints": {
            "control": "/control",
            "live": "/live", 
            "chroma": "/chroma"
        }
    }

@app.get("/")
def root():
    return RedirectResponse(url="/control")


@app.get("/control", response_class=HTMLResponse)
def control(request: Request):
    return templates.TemplateResponse("control.html", {"request": request, "lang": LANG})


@app.post("/set_language")
def set_language(lang: str = Form(...)):
    global LANG
    LANG = lang
    return RedirectResponse(url="/control", status_code=303)


@app.post("/start")
async def start(device: Optional[int] = Form(None)):
    global SESSION
    if SESSION is not None:
        return {"status": "already_running"}
    sid = session_stamp()
    SESSION = TranscriptionSession(lang=LANG, session_id=sid)
    SESSION.start(device=device)
    async def broadcaster_async():
        while SESSION is not None:
            results = SESSION.poll()
            if results:
                payload = {"type": "segments", "items": [{"id": r.segment_id, "text": r.text} for r in results]}
                await manager.broadcast_text(json.dumps(payload))
            await asyncio.sleep(0.1)
    asyncio.create_task(broadcaster_async())
    return {"status": "started", "session": sid}


@app.post("/stop")
def stop():
    global SESSION
    if SESSION is None:
        return {"status": "not_running"}
    SESSION.stop()
    sid = SESSION.session_id
    SESSION = None
    return {"status": "stopped", "session": sid}


@app.post("/after")
async def after():
    if SESSION is not None:
        return {"status": "busy", "message": "Stopp live-teksting først."}
    base = Path("data/transcripts")
    all_sessions = sorted([p for p in base.iterdir() if p.is_dir()], key=os.path.getmtime, reverse=True)
    if not all_sessions:
        return {"status": "no_session", "message": "Ingen tidligere økter funnet."}
    latest_sid = all_sessions[0].name
    rec_dir, txt_dir = session_paths(latest_sid)
    audio_files = []
    if (rec_dir / "session.wav").exists():
        audio_files = [rec_dir / "session.wav"]
    else:
        audio_files = sorted(rec_dir.glob("part_*.wav"))
    if not audio_files:
        return {"status": "no_audio"}
    texts = await transcribe_many_with_progress([str(p) for p in audio_files], lang=LANG, ws_manager=manager)
    final_path = txt_dir / "final.txt"
    final_path.write_text("\n".join(texts).strip(), encoding="utf-8")
    await manager.broadcast_text(json.dumps({"type": "status", "text": "Ferdig! Resultatet er klart."}))
    return {"status": "ok", "final": str(final_path)}


@app.post("/summarize")
async def summarize():
    if SESSION is not None:
        return {"status": "busy"}
    latest = sorted((Path("data/transcripts").glob("*/final.txt")), reverse=True)
    if not latest:
        return {"status": "no_transcript"}
    final_path = latest[0]
    await manager.broadcast_text(json.dumps({"type": "status", "text": "Fant transkripsjon. Sender til Ollama for oppsummering..."}))
    md = await asyncio.to_thread(summarize_to_markdown, final_path, lang=LANG)
    if md is None:
        await manager.broadcast_text(json.dumps({"type": "status", "text": "Feil under oppsummering."}))
        return {"status": "error"}
    await manager.broadcast_text(json.dumps({"type": "status", "text": "Referat generert!"}))
    return {"status": "ok", "md": str(md)}


@app.get("/download/{kind}")
def download(kind: str):
    base = Path("data/transcripts")
    if kind not in {"live", "final", "md"}:
        return {"status": "unknown"}
    mapping = {"live": "live.txt", "final": "final.txt", "md": "final.md"}
    media_types = {"live": "text/plain", "final": "text/plain", "md": "text/markdown"}
    latest_files = sorted((base.glob(f"*/{mapping[kind]}")), reverse=True)
    if not latest_files:
        return {"status": "not_found"}
    latest_path = latest_files[0]
    filename = latest_path.name
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return FileResponse(latest_path, headers=headers, media_type=media_types.get(kind))


@app.get("/live", response_class=HTMLResponse)
def live(request: Request):
    return templates.TemplateResponse("live.html", {"request": request})


@app.get("/chroma", response_class=HTMLResponse)
def chroma(request: Request):
    return templates.TemplateResponse("chroma.html", {"request": request})


@app.websocket("/ws")
async def ws(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(ws)
    except Exception:
        manager.disconnect(ws)