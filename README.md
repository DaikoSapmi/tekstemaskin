# Tekstemaskin - Real-time Speech-to-Text with translation capabilities

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.112.0-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A sophisticated real-time speech-to-text application built with FastAPI, featuring Norwegian and Northern Sámi language support, live transcription, and AI-powered meeting summarization.

<img width="1245" height="656" alt="Skjermbilde 2025-08-10 kl  19 48 02" src="https://github.com/user-attachments/assets/e9da0534-fe3a-4923-8f32-82e6ec7be120" />


## 🚀 Features

### Core Functionality
- **Real-time transcription** with minimal latency using Whisper models
- **Multi-language support** - It transcribes from Northern Sámi, Norwegian and English to Norwegian (Bokmål/Nynorsk) or English
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

This project was developed to provide high-quality Norwegian and Northern Sámi speech recognition capabilities for meetings, presentations, and live events.

## 📋 Requirements

### System Requirements
- **Operating System**: macOS 10.15+ or Windows 10+
- **Python**: 3.10 - 3.12
- **Memory**: Minimum 8GB RAM (16GB+ recommended for optimal performance)
- **Storage**: 2GB+ free space for models and dependencies

### Audio Setup

#### macOS - BlackHole Configuration for Digital Meetings

**BlackHole** is essential for capturing both your microphone and meeting participants' audio simultaneously. 

> **💡 Smart Detection**: Tekstemaskin automatically detects if BlackHole is already installed and skips the installation step during setup.

Here's how to set it up:

1. **Install BlackHole 2ch**
   ```bash
   brew install blackhole-2ch
   ```
   Or download from [existential.audio/blackhole](https://existential.audio/blackhole/)

2. **Configure Audio MIDI Setup**
   - Open **Audio MIDI Setup** (Applications → Utilities → Audio MIDI Setup)
   - In the left sidebar, you should see **BlackHole 2ch** listed

3. **Create Multi-Output Device**
   - Click the **+** button at the bottom left
   - Select **Create Multi-Output Device**
   - Name it "Meeting Audio" or similar
   - Check both **Built-in Output** and **BlackHole 2ch**
   - Set **Built-in Output** as the master device

4. **Set System Audio Output**
   - Go to **System Preferences → Sound → Output**
   - Select your **Multi-Output Device** (e.g., "Meeting Audio")
   - This ensures system audio goes to both speakers and BlackHole

5. **Configure BlackHole Input**
   - In **Audio MIDI Setup**, select **BlackHole 2ch**
   - Set **Format** to **2ch-16bit-48kHz** (or match your system)
   - Ensure **Drift Correction** is enabled

6. **Test the Setup**
   - Play audio from any application
   - You should hear it through speakers AND it should be available as input in Tekstemaskin

**Pro Tips for Digital Meetings:**
- **Zoom/Teams**: Audio will automatically route through BlackHole
- **Browser meetings**: Ensure browser audio isn't muted
- **Volume levels**: Adjust system volume to balance microphone vs. participant audio
- **Latency**: BlackHole adds minimal latency (~1-2ms) which is negligible for transcription

#### Windows
- **"Stereo Mix"** or virtual audio cable (e.g., VB-Audio)

## 🛠️ Installation

### Quick Start (macOS)

```bash
# Clone the repository
git clone https://github.com/DaikoSapmi/tekstemaskin.git
cd tekstemaskin

# Make the script executable and run
chmod +x run_mac.sh
```

### First-Time Setup

When you run Tekstemaskin for the first time, it will guide you through:

1. **Audio Setup Guide** - Interactive setup for BlackHole and audio configuration
2. **Ollama Installation** - Optional AI summarization setup
3. **Environment Configuration** - Automatic .env file creation

After the first setup, Tekstemaskin will start directly without showing the setup guide.

**To reset setup and run the guide again:**
```bash
python -m app.__main__ --reset-setup
```

**To see available commands:**
```bash
python -m app.__main__ --help
```
./run_mac.sh
```

### Quick Start (Windows)

1. Right-click `run_windows.ps1` → "Run with PowerShell"
2. Allow execution if prompted by Windows Security

The scripts will automatically:
- Install system dependencies
- Create a Python virtual environment
- Install Python packages
- Check/create `.env` file from `dot_env.example`
- Verify Ollama installation for AI summaries
- Start the server and wait for it to be ready
- Open browser automatically when ready

### Manual Installation

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python -m app

**Note**: The manual startup now includes:
- Automatic `.env` file creation from `dot_env.example`
- Ollama installation check and setup assistance
- Smart server startup with health checks
- Automatic browser opening when ready
```

## 🤖 AI Summarization Setup

Tekstemaskin can generate meeting summaries using AI models. You have three options:

### Option 1: Local Ollama (Recommended for Privacy)

**Ollama** allows you to run large language models locally on your machine, keeping your data private and avoiding API costs.

#### macOS Installation
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
ollama serve

# Download a Norwegian-optimized model (in a new terminal)
ollama pull gpt-oss:20B
# Alternative models:
# ollama pull llama3.2:3b    # Smaller, faster
# ollama pull mistral:7b     # Good balance of speed/quality
```

#### Windows Installation
1. Download from [ollama.ai/download](https://ollama.ai/download)
2. Run the installer
3. Open PowerShell and run:
   ```powershell
   ollama serve
   ollama pull gpt-oss:20B
   ```

#### Linux Installation
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start service and download model
ollama serve
ollama pull gpt-oss:20B
```

#### Verify Ollama Installation
```bash
# Check if Ollama is running
ollama list

# Test the model
ollama run gpt-oss:20B "Write a short greeting in Norwegian"
```

### Option 2: OpenAI API
- Get an API key from [platform.openai.com](https://platform.openai.com)
- Add to your `.env` file: `OPENAI_API_KEY=your_key_here`

### Option 3: Azure OpenAI
- Configure your Azure OpenAI endpoint in `.env`
- Set `AZURE_API_KEY`, `AZURE_ENDPOINT`, and `AZURE_DEPLOYMENT`

**Note**: Commercial APIs require internet connection and may incur costs per request.

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

# Ollama Configuration Details
# OLLAMA_BASE_URL: Default Ollama endpoint (usually http://localhost:11434/v1)
# OLLAMA_MODEL: Model name (gpt-oss:20B, llama3.2:3b, mistral:7b, etc.)
# OPENAI_MODEL: OpenAI model name (gpt-4o-mini, gpt-4, etc.)
```

## 🚀 **Smart Startup Features**

Tekstemaskin now includes intelligent startup features that make setup and usage seamless:

### **Automatic Environment Setup**
- **`.env` File Creation**: Automatically copies `dot_env.example` to `.env` if missing
- **Configuration Validation**: Ensures all required settings are available
- **User Guidance**: Provides helpful tips for customizing settings

### **Ollama Integration Check**
- **Installation Detection**: Automatically detects if Ollama is installed
- **Installation Assistance**: Offers to install Ollama during startup
- **Cross-Platform Support**: macOS (Homebrew), Windows (winget), Linux (install script)
- **Model Management**: Automatically downloads default models
- **Service Startup**: Ensures Ollama service is running

### **Smart Server Startup**
- **Health Check Monitoring**: Waits for server to be fully ready
- **Progress Indicators**: Shows startup progress with clear status messages
- **Automatic Browser Opening**: Only opens browser when server is confirmed ready
- **Fallback Handling**: Graceful handling of edge cases and timeouts

### **Startup Flow**
```
🚀 Starting Tekstemaskin server...
📋 .env file not found, copying from dot_env.example...
✅ .env file created successfully!
🤖 Checking Ollama installation...
✅ Ollama is installed: ollama version is 0.11.4
🤖 Ollama is ready for AI summaries!
============================================================
🚀 STARTING TEKSTEMASKIN SERVER
============================================================
🔍 Checking if server is ready...
✅ Server is ready! healthy
🌐 Browser opened: http://localhost:8000/control
🎉 Tekstemaskin is ready to use!
```

## 🎯 Usage

### 1. Control Panel
Navigate to `http://localhost:8000/control` to:
- Select language (Norwegian Bokmål/Nynorsk or English)
- Choose audio input device:
  - **BlackHole 2ch** (macOS) - Captures system audio + microphone
  - **Default microphone** - Captures only microphone input
  - **Other audio devices** - Any available audio input
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

### Speech Recognition
- **GPU Acceleration**: Use CUDA (NVIDIA) or MPS (Apple Silicon) for faster processing
- **Model Selection**: `NbAiLab/nb-whisper-large` provides excellent Norwegian accuracy
- **Audio Quality**: Use 16kHz sample rate for optimal Whisper performance
- **Chunk Size**: 4-second chunks with 0.5s overlap balance speed and accuracy

### AI Summarization
- **Ollama Models**: Choose based on your hardware capabilities:
  - **gpt-oss:20B**: Best quality, requires 16GB+ RAM
  - **llama3.2:3b**: Fast, good quality, works with 8GB RAM
  - **mistral:7b**: Balanced performance, needs 12GB+ RAM
- **Commercial APIs**: Faster processing but requires internet and may incur costs
- **Batch Processing**: Process multiple transcripts together for efficiency

## 🔍 Troubleshooting

### Common Issues

**Audio not detected:**
- Ensure audio capture software is running (BlackHole, VB-Audio)
- Check system audio permissions
- Verify microphone access in system settings

**BlackHole not working (macOS):**
- Verify BlackHole 2ch is installed and enabled in Audio MIDI Setup
- Check that Multi-Output Device is set as system audio output
- Restart applications (Zoom, Teams, etc.) after BlackHole setup
- Ensure BlackHole 2ch appears in Tekstemaskin's device list
- Try restarting the audio system: `sudo killall coreaudiod`

**Ollama not working:**
- Ensure Ollama service is running: `ollama serve`
- Check if model is downloaded: `ollama list`
- Verify Ollama is accessible: `curl http://localhost:11434/v1/models`
- Check firewall settings blocking port 11434
- Restart Ollama service if needed: `ollama stop && ollama serve`
- Ensure sufficient RAM for the model (20B models need 16GB+ RAM)

**Model download fails:**
- Check internet connection
- Ensure sufficient disk space
- Try manual download from Hugging Face

**Performance issues:**
- Use GPU acceleration if available
- Reduce chunk size for lower latency
- Close other resource-intensive applications

**Startup issues:**
- **Browser opens too early**: The app now waits for server readiness before opening
- **Health check timeout**: Server may take longer on slower systems, wait up to 30 seconds
- **Ollama installation fails**: Check internet connection and system permissions
- **Port 8000 already in use**: Stop other applications using the port or change PORT in .env
- **Permission denied**: Ensure scripts have execute permissions (`chmod +x run_mac.sh`)

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
- I am really sorry to inform you that you are on your own, but you are of course free to use it, improve it and abuse it as you want!

---

**Built with ❤️ for Sápmi**
