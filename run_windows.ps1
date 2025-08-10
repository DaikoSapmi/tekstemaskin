# Sørger for at skriptet stopper hvis en kommando feiler
$ErrorActionPreference = "Stop"

# --- STEG 1: Sjekk og installer systemavhengigheter med Chocolatey ---
Write-Host "› Sjekker systemavhengigheter (Chocolatey)..." -ForegroundColor Green

# Sjekk om Chocolatey er installert
if (-not (Get-Command choco -ErrorAction SilentlyContinue)) {
    Write-Host "FEIL: Chocolatey er ikke installert. Vennligst installer Chocolatey først." -ForegroundColor Red
    Write-Host "Se: https://chocolatey.org/install"
    exit 1
}

# Sjekk om libsndfile er installert, installer hvis ikke
$libsndfile = choco list --local-only libsndfile
if (-not $libsndfile) {
    Write-Host "  - libsndfile ikke funnet. Installerer med Chocolatey..."
    choco install libsndfile -y
} else {
    Write-Host "  - libsndfile er allerede installert."
}


# --- STEG 2: Opprett og aktiver virtuelt Python-miljø ---
Write-Host "`n› Setter opp virtuelt Python-miljø (.venv)..." -ForegroundColor Green
if (-not (Test-Path ".venv")) {
  python -m venv .venv
}
# Aktiver det virtuelle miljøet for denne økten
.\.venv\Scripts\Activate.ps1


# --- STEG 3: Installer Python-pakker ---
Write-Host "`n› Installerer/oppdaterer Python-pakker fra requirements.txt..." -ForegroundColor Green
python -m pip install --upgrade pip wheel
pip install -r requirements.txt


# --- STEG 4: Opprett datakataloger (hvis de ikke finnes) ---
Write-Host "`n› Sikrer at datakataloger eksisterer..." -ForegroundColor Green
New-Item -ItemType Directory -Force -Path "data\recordings" | Out-Null
New-Item -ItemType Directory -Force -Path "data\transcripts" | Out-Null


# --- STEG 5: Start applikasjonen ---
Write-Host "`n› Starter applikasjonen..." -ForegroundColor Green
Write-Host "💡 The app will now:" -ForegroundColor Cyan
Write-Host "   • Check/create .env file from dot_env.example" -ForegroundColor Cyan
Write-Host "   • Verify Ollama installation for AI summaries" -ForegroundColor Cyan
Write-Host "   • Start the server and wait for it to be ready" -ForegroundColor Cyan
Write-Host "   • Open browser automatically when ready" -ForegroundColor Cyan
Write-Host "" -ForegroundColor Cyan
# Bruker 'python -m app' for konsistens med Mac-skriptet
python -m app