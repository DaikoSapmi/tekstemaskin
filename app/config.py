# app/config.py
from dataclasses import dataclass
import os
from dotenv import load_dotenv  # <-- 1. NY IMPORT

load_dotenv()  # <-- 2. LASTER .ENV-FILEN

@dataclass
class Settings:
    # ASR Innstillinger
    default_lang: str = os.getenv("APP_DEFAULT_LANG", "no")
    asr_model: str = os.getenv("ASR_MODEL", "NbAiLab/nb-whisper-large")
    asr_device: str = os.getenv("ASR_DEVICE", "auto")

    # Audio Innstillinger
    sample_rate: int = int(os.getenv("SAMPLE_RATE", "16000"))
    chunk_seconds: float = float(os.getenv("CHUNK_SECONDS", "4"))
    overlap_seconds: float = float(os.getenv("OVERLAP_SECONDS", "0.5"))

    # --- LLM Innstillinger ---
    ollama_base_url: str | None = os.getenv("OLLAMA_BASE_URL")
    ollama_model: str | None = os.getenv("OLLAMA_MODEL")

    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    openai_base_url: str | None = os.getenv("OPENAI_BASE_URL")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    azure_endpoint: str | None = os.getenv("AZURE_OPENAI_ENDPOINT")
    azure_api_key: str | None = os.getenv("AZURE_OPENAI_API_KEY")
    azure_deployment: str | None = os.getenv("AZURE_OPENAI_DEPLOYMENT")

settings = Settings()