# Tekstemaskin - Real-time Speech-to-Text with Norwegian Support

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.112.0-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A sophisticated real-time speech-to-text application built with FastAPI, featuring Norwegian and Northern Sámi language support, live transcription, and AI-powered meeting summarization.

## 🚀 Features

### Core Functionality
- **Real-time transcription** with minimal latency using Whisper models
- **Multi-language support** - Norwegian (Bokmål/Nynorsk) and English
- **Live streaming** with WebSocket support for real-time updates
- **Chroma key view** optimized for OBS/streaming with green screen background
- **Automatic audio recording** with session management

### Advanced Features
- **AI-powered summarization** using multiple LLM providers:
  - Local Ollama models
  - OpenAI API
  - Azure OpenAI
- **High-quality offline processing** for post-meeting refinement
- **Flexible audio configuration** with customizable chunk sizes and overlap
- **Cross-platform support** for macOS and Windows

## 👨‍💻 Author

**Rune Fjellheim** - [DaikoSapmi](https://github.com/DaikoSapmi)

This project was developed to provide high-quality Norwegian speech recognition capabilities for meetings, presentations, and live events.

## 📋 Requirements

### System Requirements
- **Operating System**: macOS 10.15+ or Windows 10+
- **Python**: 3.10 - 3.12
- **Memory**: Minimum 8GB RAM (16GB+ recommended for optimal performance)
- **Storage**: 2GB+ free space for models and dependencies

### Audio Setup
- **macOS**: [BlackHole 2ch](https://existential.audio/blackhole/) for system audio capture
- **Windows**: "Stereo Mix" or virtual audio cable (e.g., VB-Audio)

## 🛠️ Installation

### Quick Start (macOS)

```bash
# Clone the repository
git clone https://github.com/DaikoSapmi/tekstemaskin.git
cd tekstemaskin

# Make the script executable and run
chmod +x run_mac.sh
./run_mac.sh
```

### Quick Start (Windows)

1. Right-click `run_windows.ps1` → "Run with PowerShell"
2. Allow execution if prompted by Windows Security

The scripts will automatically:
- Install system dependencies
- Create a Python virtual environment
- Install Python packages
- Launch the application

### Manual Installation

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python -m app
```

## ⚙️ Configuration

Copy `.env.example` to `.env` and customize your settings:

```bash
cp dot_env.example .env
```

### Key Configuration Options

```env
# Speech Recognition
ASR_MODEL=NbAiLab/nb-whisper-large
ASR_DEVICE=mps        # auto | cpu | mps | cuda
APP_DEFAULT_LANG=no   # no | nn | en

# Audio Processing
SAMPLE_RATE=16000
CHUNK_SECONDS=4
OVERLAP_SECONDS=0.5

# AI Summarization
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_MODEL=gpt-oss:20B
OPENAI_API_KEY=your_key_here
```

## 🎯 Usage

### 1. Control Panel
Navigate to `http://localhost:8000/control` to:
- Select language (Norwegian Bokmål/Nynorsk or English)
- Choose audio input device
- Start/stop transcription sessions

### 2. Live View
- **Live Tab**: Real-time transcription with highlighting
- **Chroma Tab**: Green screen optimized view for OBS integration

### 3. Post-Processing
- **Full Transcription**: High-quality offline processing
- **AI Summarization**: Generate meeting minutes in Markdown format
- **Download**: Export transcripts and summaries

## 🔧 OBS Integration

1. Add a "Browser Source" in OBS
2. Set URL to: `http://localhost:8000/chroma`
3. Adjust font size and contrast in the control panel
4. Enable chroma key in OBS for transparent background

## 📁 Project Structure

```
tekstemaskin/
├── app/                    # Application source code
│   ├── main.py            # FastAPI application entry point
│   ├── stt_engine.py      # Speech-to-text engine
│   ├── summary_llm.py     # AI summarization service
│   ├── config.py          # Configuration management
│   ├── templates/         # HTML templates
│   └── static/            # CSS, JavaScript, and assets
├── data/                  # Session data
│   ├── recordings/        # Audio recordings per session
│   └── transcripts/       # Live and final transcriptions
├── run_mac.sh            # macOS setup script
├── run_windows.ps1       # Windows setup script
└── requirements.txt       # Python dependencies
```

## 🚀 Performance Tips

- **GPU Acceleration**: Use CUDA (NVIDIA) or MPS (Apple Silicon) for faster processing
- **Model Selection**: `NbAiLab/nb-whisper-large` provides excellent Norwegian accuracy
- **Audio Quality**: Use 16kHz sample rate for optimal Whisper performance
- **Chunk Size**: 4-second chunks with 0.5s overlap balance speed and accuracy

## 🔍 Troubleshooting

### Common Issues

**Audio not detected:**
- Ensure audio capture software is running (BlackHole, VB-Audio)
- Check system audio permissions
- Verify microphone access in system settings

**Model download fails:**
- Check internet connection
- Ensure sufficient disk space
- Try manual download from Hugging Face

**Performance issues:**
- Use GPU acceleration if available
- Reduce chunk size for lower latency
- Close other resource-intensive applications

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **NbAiLab** for the excellent Norwegian Whisper model
- **OpenAI** for the Whisper architecture
- **FastAPI** team for the excellent web framework
- **PyTorch** community for the machine learning ecosystem

## 📞 Support

For support, questions, or feature requests:
- Open an issue on GitHub
- Contact the author at [rune@fjellheim.tv](mailto:rune@fjellheim.tv)

---

**Built with ❤️ for the Sámi community**
