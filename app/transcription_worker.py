# transcription_worker.py
from __future__ import annotations
import json
from pathlib import Path
from typing import Optional, List

from .stt_engine import SpeechToTextEngine, LiveResult
from .utils import session_paths
from .offline_asr import transcribe_many


class TranscriptionSession:
    def __init__(self, lang: str, session_id: str):
        self.lang = lang
        self.session_id = session_id
        self.rec_dir, self.txt_dir = session_paths(session_id)
        self.engine: Optional[SpeechToTextEngine] = None
        self.live_buffer: list[dict] = []

    def start(self, device: Optional[int] = None):
        self.engine = SpeechToTextEngine(self.lang, self.session_id)
        self.engine.start(device=device)

    def stop(self):
        if self.engine:
            self.engine.stop()
            self._persist_live()

    def poll(self) -> list[LiveResult]:
        results: list[LiveResult] = []
        if not self.engine:
            return results
        while not self.engine.out_q.empty():
            r = self.engine.out_q.get()
            self.live_buffer.append({"id": r.segment_id, "text": r.text})
            results.append(r)
        return results

    def _persist_live(self):
        """Lagrer den kontinuerlige live-teksten."""
        out_json = Path(self.txt_dir) / "live_segments.json"
        out_txt = Path(self.txt_dir) / "live.txt"
        out_json.write_text(json.dumps(self.live_buffer, ensure_ascii=False, indent=2), encoding="utf-8")
        # Live-tekst skjøtes sammen uten linjeskift for en kontinuerlig strøm
        out_txt.write_text(" ".join(s.get("text", "").strip() for s in self.live_buffer), encoding="utf-8")

    def after_the_fact(self) -> Path:
        """
        Transkriberer storfila (session.wav eller part_*.wav) med offline-ASR
        for høyere nøyaktighet, og skriver resultatet til final.txt.
        """
        final_path = Path(self.txt_dir) / "final.txt"

        # Finn storfil(er)
        audio_files: List[Path] = []
        session_wav = self.rec_dir / "session.wav"
        if session_wav.exists():
            audio_files = [session_wav]
        else:
            audio_files = sorted(self.rec_dir.glob("part_*.wav"))

        if not audio_files:
            # Fallback: kopier live.txt slik at knappen fortsatt gir noe
            print("[worker] Ingen stor lydfil funnet. Kopierer live.txt til final.txt som fallback.")
            live_path = Path(self.txt_dir) / "live.txt"
            final_text = live_path.read_text(encoding="utf-8") if live_path.exists() else ""
            final_path.write_text(final_text, encoding="utf-8")
            return final_path

        # Kjør grundig transkribering
        texts = transcribe_many([str(p) for p in audio_files], lang=self.lang)
        # Bli med transkriberte deler med linjeskift for lesbarhet
        final_path.write_text("\n".join(texts).strip(), encoding="utf-8")
        return final_path