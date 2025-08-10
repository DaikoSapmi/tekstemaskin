# app/offline_asr.py
from __future__ import annotations
import os
from pathlib import Path
from typing import List
from functools import lru_cache
import json
import asyncio

import torch
import torchaudio
from transformers import WhisperProcessor, WhisperForConditionalGeneration

from .config import settings
from .stt_engine import pick_device

# Anbefalinger for offline-transkribering
OFFLINE_NUM_BEAMS = int(os.getenv("OFFLINE_NUM_BEAMS", "5") or 5)

@lru_cache(maxsize=1)
def _build_asr_components():
    """Bygger og gjenbruker ASR-modell og prosessor."""
    device = pick_device()
    print(f"[offline_asr] Laster modell '{settings.asr_model}' til enhet '{device}'...")
    
    processor = WhisperProcessor.from_pretrained(settings.asr_model)
    model = WhisperForConditionalGeneration.from_pretrained(settings.asr_model).to(device)
    model.config.forced_decoder_ids = None
        
    print("[offline_asr] Modell lastet.")
    return model, processor, device

# Denne funksjonen beholdes som en fallback, i tilfelle den trengs et annet sted
def transcribe_many(paths: List[str], lang: str) -> List[str]:
    """Transkriberer filer uten fremdriftsrapportering."""
    if not paths:
        return []
    if lang == "nb":
        lang = "no"

    model, processor, device = _build_asr_components()
    texts: List[str] = []
    
    for p_str in paths:
        # Denne enklere versjonen splitter også filen manuelt for robusthet
        waveform, sample_rate = torchaudio.load(p_str)
        if sample_rate != 16000:
            resampler = torchaudio.transforms.Resample(sample_rate, 16000)
            waveform = resampler(waveform)
        
        chunk_size_frames = 30 * 16000
        num_chunks = torch.ceil(torch.tensor(waveform.shape[1] / chunk_size_frames)).int().item()
        
        full_transcription = []
        for chunk_idx in range(num_chunks):
            start_frame = chunk_idx * chunk_size_frames
            end_frame = start_frame + chunk_size_frames
            chunk_waveform = waveform[:, start_frame:end_frame]
            
            input_features = processor(chunk_waveform.squeeze().numpy(), sampling_rate=16000, return_tensors="pt").input_features.to(device)
            generate_args = {"language": lang, "task": "transcribe", "num_beams": OFFLINE_NUM_BEAMS}
            predicted_ids = model.generate(input_features, **generate_args)
            result_text = processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]
            full_transcription.append(result_text.strip())
            
        texts.append(" ".join(full_transcription))
    return texts

# NY async-funksjon med progress-rapportering
async def transcribe_many_with_progress(paths: List[str], lang: str, ws_manager) -> List[str]:
    """
    Transkriberer filer og sender fremdriftsoppdateringer via en WebSocket-manager.
    """
    if not paths:
        return []

    if lang == "nb":
        lang = "no"

    model, processor, device = _build_asr_components()
    texts: List[str] = []
    
    total_files = len(paths)
    for i, p_str in enumerate(paths, start=1):
        path = Path(p_str)
        try:
            info = await asyncio.to_thread(torchaudio.info, path)
            dur = int(info.num_frames / info.sample_rate)
            
            await ws_manager.broadcast_text(json.dumps({
                "type": "status", 
                "text": f"Starter behandling av {path.name} ({dur//60:02d}:{dur%60:02d})..."
            }))

            waveform, sample_rate = await asyncio.to_thread(torchaudio.load, path)
            if sample_rate != 16000:
                resampler = torchaudio.transforms.Resample(sample_rate, 16000)
                waveform = resampler(waveform)

            chunk_size_frames = 30 * 16000
            num_chunks = torch.ceil(torch.tensor(waveform.shape[1] / chunk_size_frames)).int().item()
            
            full_transcription = []
            for chunk_idx in range(num_chunks):
                # Oppdater status for hver bit
                await ws_manager.broadcast_text(json.dumps({
                    "type": "status", 
                    "text": f"Behandler bit {chunk_idx + 1} av {num_chunks}..."
                }))
                
                start_frame = chunk_idx * chunk_size_frames
                end_frame = start_frame + chunk_size_frames
                chunk_waveform = waveform[:, start_frame:end_frame]
                
                # Forbered input-data
                input_features = processor(
                    chunk_waveform.squeeze().numpy(), 
                    sampling_rate=16000, 
                    return_tensors="pt"
                ).input_features.to(device)

                # Definer genereringsargumenter
                generate_args = {"language": lang, "task": "transcribe", "num_beams": OFFLINE_NUM_BEAMS}
                
                # Selve modellkallet er blokkerende, så vi kjører det i en egen tråd
                predicted_ids = await asyncio.to_thread(model.generate, input_features, **generate_args)

                result_text = processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]
                full_transcription.append(result_text.strip())

            texts.append(" ".join(full_transcription))
            await ws_manager.broadcast_text(json.dumps({"type": "status", "text": f"Ferdig med {path.name}."}))

        except Exception as e:
            error_msg = f"FEIL ved behandling av {path.name}: {e}"
            print(f"[offline_asr] {error_msg}")
            texts.append(error_msg)
            await ws_manager.broadcast_text(json.dumps({"type": "status", "text": error_msg}))
            
    return texts