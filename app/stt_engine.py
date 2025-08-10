# app/stt_engine.py
from __future__ import annotations

import os
import math
import queue
import threading
import time
from dataclasses import dataclass
from typing import Optional

import numpy as np
import sounddevice as sd
import torch
from transformers import WhisperProcessor, WhisperForConditionalGeneration
from scipy.io.wavfile import write as wav_write

from .config import settings
from .utils import session_paths

# Konfig
SAVE_SEGMENTS = os.getenv("SAVE_SEGMENTS", "0").strip().lower() in {"1", "true", "yes"}
try:
    BIGFILE_ROTATE_MIN = int(os.getenv("BIGFILE_ROTATE_MIN", "0").strip() or "0")
except ValueError:
    BIGFILE_ROTATE_MIN = 0

@dataclass
class LiveResult:
    text: str
    is_final: bool
    segment_id: int

def pick_device():
    if settings.asr_device and settings.asr_device.lower() != "auto":
        d = settings.asr_device.lower()
        if d == "cuda" and torch.cuda.is_available():
            return "cuda:0"
        return d
    try:
        if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
            return "mps"
    except Exception:
        pass
    if torch.cuda.is_available():
        return "cuda:0"
    return "cpu"

class BigFileWriter:
    def __init__(self, out_dir, sample_rate: int, rotate_minutes: int = 0):
        from wave import open as wave_open
        self.wave_open = wave_open
        self.out_dir = out_dir
        self.sr = sample_rate
        self.rotate_frames = int(sample_rate * 60 * rotate_minutes) if rotate_minutes > 0 else None
        self.q: "queue.Queue[np.ndarray]" = queue.Queue(maxsize=256)
        self._stop = threading.Event()
        self.fh = None
        self.idx = 0
        self.frames_written = 0
        self.thr: Optional[threading.Thread] = None

    def _open_new(self):
        if self.fh:
            try:
                self.fh.close()
            except Exception:
                pass
        name = "session.wav" if self.rotate_frames is None else f"part_{self.idx:02d}.wav"
        path = (self.out_dir / name).as_posix()
        self.fh = self.wave_open(path, "wb")
        self.fh.setnchannels(1)
        self.fh.setsampwidth(2)
        self.fh.setframerate(self.sr)
        self.frames_written = 0

    def start(self):
        self._open_new()
        self.thr = threading.Thread(target=self._worker, daemon=True)
        self.thr.start()

    def stop(self):
        self._stop.set()
        try:
            while True:
                f32 = self.q.get_nowait()
                pcm16 = np.clip(f32 * 32767.0, -32768, 32767).astype(np.int16)
                if self.fh:
                    self.fh.writeframes(pcm16.tobytes())
                    self.frames_written += len(pcm16)
        except queue.Empty:
            pass
        if self.thr and self.thr.is_alive():
            self.thr.join(timeout=2)
        if self.fh:
            try:
                self.fh.close()
            finally:
                self.fh = None

    def enqueue_float(self, f32: np.ndarray):
        try:
            self.q.put_nowait(f32.copy())
        except queue.Full:
            pass

    def _worker(self):
        while not self._stop.is_set():
            try:
                f32 = self.q.get(timeout=0.2)
            except queue.Empty:
                continue
            pcm16 = np.clip(f32 * 32767.0, -32768, 32767).astype(np.int16)
            if self.fh:
                self.fh.writeframes(pcm16.tobytes())
                self.frames_written += len(pcm16)
                if self.rotate_frames is not None and self.frames_written >= self.rotate_frames:
                    self.idx += 1
                    self._open_new()

class SpeechToTextEngine:
    def __init__(self, lang_code: str, session_id: str):
        self.lang_code = "no" if lang_code == "nb" else lang_code
        self.session_id = session_id
        self.rec_dir, self.txt_dir = session_paths(session_id)
        self.sample_rate = settings.sample_rate
        self.chunk_seconds = settings.chunk_seconds
        self.overlap_seconds = settings.overlap_seconds
        self.stream: Optional[sd.InputStream] = None
        self.seg_q: "queue.Queue[np.ndarray]" = queue.Queue()
        self.out_q: "queue.Queue[LiveResult]" = queue.Queue()
        self._stop = threading.Event()
        self._worker_thr: Optional[threading.Thread] = None
        self.big_writer = BigFileWriter(self.rec_dir, self.sample_rate, BIGFILE_ROTATE_MIN)
        self.big_writer.start()

        # Modernisert ASR-oppsett
        device = pick_device()
        self.device = device
        print(f"[live_engine] Laster modell '{settings.asr_model}' til enhet '{device}'...")
        self.processor = WhisperProcessor.from_pretrained(settings.asr_model)
        self.model = WhisperForConditionalGeneration.from_pretrained(settings.asr_model).to(device)
        self.model.config.forced_decoder_ids = None # Anbefalt for ren transkribering
        print("[live_engine] Modell lastet.")
        
        self._last_level_log = time.time()

    def _audio_callback(self, indata, frames, time_info, status):
        if status: pass
        mono = indata.mean(axis=1) if indata.ndim > 1 else indata
        self.big_writer.enqueue_float(mono)
        try:
            self.seg_q.put_nowait(mono.copy())
        except queue.Full:
            pass
        now = time.time()
        if now - self._last_level_log > 2.0:
            rms = float(np.sqrt(np.mean(np.square(mono))) + 1e-12)
            dbfs = 20.0 * math.log10(rms) if rms > 0 else -120.0
            print(f"[audio] nivå ~ {dbfs:.1f} dBFS")
            self._last_level_log = now

    def start(self, device: Optional[int] = None):
        blocksize = int(self.sample_rate * 0.5)
        self.stream = sd.InputStream(
            samplerate=self.sample_rate, channels=1, dtype="float32",
            callback=self._audio_callback, blocksize=blocksize, device=device
        )
        self.stream.start()
        self._worker_thr = threading.Thread(target=self._worker, daemon=True)
        self._worker_thr.start()

    def stop(self):
        self._stop.set()
        if self.stream:
            try:
                self.stream.stop()
                self.stream.close()
            except Exception as e:
                print(f"Feil ved stopping av lydstrøm: {e}")
        if self._worker_thr and self._worker_thr.is_alive():
            self._worker_thr.join(timeout=2)
        self.big_writer.stop()

    def _worker(self):
        chunk_len = int(self.sample_rate * self.chunk_seconds)
        overlap_len = int(self.sample_rate * self.overlap_seconds)
        if overlap_len >= chunk_len:
            overlap_len = max(0, chunk_len // 4)

        buf = np.zeros(0, dtype=np.float32)
        segment_id = 0

        while not self._stop.is_set():
            try:
                inblock = self.seg_q.get(timeout=0.2)
            except queue.Empty:
                continue

            buf = np.concatenate([buf, inblock])

            while len(buf) >= chunk_len:
                segment = buf[:chunk_len]
                buf = buf[chunk_len - overlap_len:]

                if SAVE_SEGMENTS:
                    wav_path = self.rec_dir / f"seg_{segment_id:06d}.wav"
                    pcm16 = np.clip(segment * 32767.0, -32768, 32767).astype(np.int16)
                    wav_write(wav_path.as_posix(), self.sample_rate, pcm16)

                text = ""
                try:
                    # Modernisert ASR-kall
                    input_features = self.processor(
                        segment, sampling_rate=self.sample_rate, return_tensors="pt"
                    ).input_features.to(self.device)
                    
                    predicted_ids = self.model.generate(input_features, language=self.lang_code, task="transcribe")
                    text = self.processor.batch_decode(predicted_ids, skip_special_tokens=True)[0].strip()
                
                except Exception as e:
                    print(f"[asr] feilet segment {segment_id}: {e}")
                
                self.out_q.put(LiveResult(text=text, is_final=True, segment_id=segment_id))
                segment_id += 1