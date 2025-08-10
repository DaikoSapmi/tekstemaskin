# live-tekstemaskin – nb-whisper-large

En enkel og brukervennlig løsning for sanntids tale-til-tekst på norsk bokmål eller engelsk, med live-visning og undertekster for streaming.

## funksjoner

* **live-teksting** med lav forsinkelse i nettleser
* egen *chroma key*-visning (grønn bakgrunn) for OBS/streaming
* automatisk lagring av lydopptak per økt
* etterbehandling med høyest mulig transkriberingskvalitet
* generering av møtereferat i markdown med LLM (valgfritt)
* valg av språk ved oppstart (norsk bokmål / engelsk)

## krav

* macOS eller Windows
* Python 3.10–3.12 installert
* lydoppsett:

  * macOS: [BlackHole 2ch](https://existential.audio/blackhole/) for systemlyd + mikrofon
  * Windows: «Stereo Mix» eller virtuelt lydkabelverktøy (f.eks. VB-Audio)

> Ved første kjøring lastes modellen `NbAiLab/nb-whisper-large` fra Hugging Face (kan ta noen minutter). Senere starter programmet raskt.

## installasjon og oppstart

### macOS

```bash
chmod +x run_mac.sh
./run_mac.sh
```

### Windows

1. Høyreklikk `run_windows.ps1` → «Run with PowerShell»
2. Tillat kjøring hvis du blir spurt

Skriptet oppretter virtuelt miljø, installerer avhengigheter og starter kontrollpanelet i nettleseren.

## arbeidsflyt

1. Velg språk og lydkilde i kontrollpanelet
2. Klikk **Start live-teksting**
3. Bruk *Live*-fanen som løpende skjerm (siste utsagn markeres)
4. Bruk *Chroma*-fanen som undertekst i OBS via «Browser Source»
5. Etter møtet: kjør **Full transkribering**
6. Generer møtereferat i markdown og last ned

## mappestruktur

* `data/recordings/` – lydopptak per økt
* `data/transcripts/` – live- og endelige transkripsjoner
* `app/` – kildekode, maler og statiske filer

## tips for OBS

* Legg til en «Browser Source» og pek til `http://localhost:8000/chroma`
* Juster skriftstørrelse og kontrast i kontrollpanelet

## konfigurasjon

Kopier `.env.example` til `.env` og rediger ved behov (modell, språk, LLM-nøkler).

## lisens

Prosjektet kan brukes og tilpasses fritt.
