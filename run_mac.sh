#!/usr/bin/env bash
set -euo pipefail

# --- STEG 1: Sjekk og installer systemavhengigheter med Homebrew ---
echo "› Sjekker systemavhengigheter (Homebrew)..."

# Sjekk om Homebrew er installert
if ! command -v brew &> /dev/null; then
    echo "FEIL: Homebrew er ikke installert. Vennligst installer Homebrew først."
    echo "Se: https://brew.sh"
    exit 1
fi

# Sjekk om libsndfile er installert, installer hvis ikke
if ! brew list libsndfile &> /dev/null; then
    echo "  - libsndfile ikke funnet. Installerer med Homebrew..."
    brew install libsndfile
else
    echo "  - libsndfile er allerede installert."
fi


# --- STEG 2: Opprett og aktiver virtuelt Python-miljø ---
echo -e "\n› Setter opp virtuelt Python-miljø (.venv)..."
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi
source .venv/bin/activate


# --- STEG 3: Installer Python-pakker ---
echo -e "\n› Installerer/oppdaterer Python-pakker fra requirements.txt..."
python -m pip install -U pip wheel
pip install -r requirements.txt


# --- STEG 4: Start applikasjonen ---
echo -e "\n› Starter applikasjonen..."
echo "💡 The app will now:"
echo "   • Check/create .env file from dot_env.example"
echo "   • Verify Ollama installation for AI summaries"
echo "   • Start the server and wait for it to be ready"
echo "   • Open browser automatically when ready"
echo ""
python -m app