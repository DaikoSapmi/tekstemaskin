# app/summary_llm.py
from __future__ import annotations
from pathlib import Path
from typing import Optional
from datetime import datetime
import locale

from .config import settings

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

# Sett norsk lokal tid for datostreng
try:
    locale.setlocale(locale.LC_TIME, "nb_NO.UTF-8")
except locale.Error:
    try:
        locale.setlocale(locale.LC_TIME, "Norwegian_Norway.1252")
    except locale.Error:
        print("Advarsel: Kunne ikke sette norsk lokal tid for datoformatering.")


def summarize_to_markdown(transcript_path: Path, lang: str = "no") -> Optional[Path]:
    """
    Sender transkripsjon til en LLM for oppsummering og returnerer en Markdown-fil.
    """
    if not transcript_path.exists():
        print(f"[llm] Feil: Transkripsjonsfilen '{transcript_path}' finnes ikke.")
        return None
    text = transcript_path.read_text(encoding="utf-8")
    if not text.strip():
        print("[llm] Transkripsjonsfilen er tom, ingenting å oppsummere.")
        return None

    client = None
    model = None
    llm_service = "Ingen"

    # --- KORRIGERT LOGIKK MED SMÅ BOKSTAVER ---
    # Prioriter Ollama hvis konfigurert
    if settings.ollama_base_url and settings.ollama_model:
        if OpenAI is None:
            print("[llm] 'openai' biblioteket er ikke installert. Kjør: pip install openai")
            return None
        print(f"[llm] Bruker lokal LLM via Ollama: {settings.ollama_model}")
        client = OpenAI(
            base_url=settings.ollama_base_url,
            api_key="ollama",
        )
        model = settings.ollama_model
        llm_service = "Ollama"

    # Fallback til Azure
    elif settings.azure_api_key and settings.azure_endpoint and OpenAI:
        print(f"[llm] Bruker Azure OpenAI: {settings.azure_deployment}")
        client = OpenAI(
            api_key=settings.azure_api_key,
            base_url=f"{settings.azure_endpoint}/openai/deployments/{settings.azure_deployment}",
            api_version="2024-02-01",
        )
        model = "gpt-4o-mini"
        llm_service = "Azure OpenAI"

    # Fallback til OpenAI
    elif settings.openai_api_key and OpenAI:
        print(f"[llm] Bruker OpenAI API: {settings.openai_model}")
        client = OpenAI(api_key=settings.openai_api_key, base_url=settings.openai_base_url or None)
        model = settings.openai_model
        llm_service = "OpenAI"
    
    if not client:
        print("[llm] Ingen LLM konfigurert. Lager enkel Markdown-rapport.")
        md_content = f"# Møtereferat\n\n> LLM ikke konfigurert – genererer enkel oppsummering basert på råtekst.\n\n---\n\n{text}\n"
        out_path = transcript_path.with_suffix(".md")
        out_path.write_text(md_content, encoding="utf-8")
        return out_path
    
    # Generer dagens dato og tid i norsk format
    now_str = datetime.now().strftime("%d. %B %Y, kl. %H:%M")
    
    prompt_text = (
        "Du er en dyktig og presis assistent som lager møtereferater. "
        "Analyser følgende transkripsjon fra et møte og skriv et profesjonelt, velstrukturert og konsist møtereferat i Markdown-format.\n\n"
        "Struktur for referatet:\n"
        "1. Start med en hovedtittel (`#`) som oppsummerer møtets hovedtema.\n"
        f"2. Rett under tittelen, legg inn en undertittel (`##`) med nøyaktig denne datoen og tiden: **{now_str}**\n"
        "3. Deretter skal referatet inneholde følgende punkter med klare overskrifter (`###`):\n"
        "    - **Deltakere:** (List opp deltakere hvis de nevnes)\n"
        "    - **Saksliste/Hovedtemaer:** En kort oversikt over hva møtet handlet om.\n"
        "    - **Viktige Diskusjonspunkter:** Oppsummer de sentrale samtalene og synspunktene.\n"
        "    - **Beslutninger:** En nummerert liste over alle konkrete vedtak som ble gjort.\n"
        "    - **Aksjonspunkter:** En tabell eller en punktliste med 'Oppgave', 'Ansvarlig' og 'Frist'.\n\n"
        "Sørg for at språket er renskrevet og profesjonelt. Vær objektiv og hold deg til informasjonen fra transkripsjonen."
    )

    messages = [
        {"role": "system", "content": prompt_text},
        {"role": "user", "content": f"Her er transkripsjonen:\n\n---\n\n{text}"},
    ]

    try:
        print(f"[llm] {llm_service} oppsummering. Dette kan ta litt tid...")
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.1,
        )
        md_content = response.choices[0].message.content
        print("[llm] Oppsummering mottatt.")
    except Exception as e:
        print(f"[llm] En feil oppstod under kall til {llm_service}: {e}")
        md_content = f"# Feil ved generering av referat\n\nKunne ikke koble til {llm_service} eller en feil oppstod.\n\n**Feilmelding:**\n`{e}`\n\n**Rå-transkripsjon:**\n{text}"

    out_path = transcript_path.with_suffix(".md")
    out_path.write_text(md_content, encoding="utf-8")
    return out_path