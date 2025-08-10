from pathlib import Path
from datetime import datetime

BASE = Path("data")
RECS = BASE / "recordings"
TXTS = BASE / "transcripts"

for p in (BASE, RECS, TXTS):
    p.mkdir(parents=True, exist_ok=True)


def session_stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def session_paths(stamp: str):
    rec_dir = RECS / stamp
    txt_dir = TXTS / stamp
    rec_dir.mkdir(parents=True, exist_ok=True)
    txt_dir.mkdir(parents=True, exist_ok=True)
    return rec_dir, txt_dir