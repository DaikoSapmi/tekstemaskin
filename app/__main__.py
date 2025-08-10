import os
import webbrowser
import uvicorn
import time
import requests
import shutil
import subprocess
import sys
import platform
from threading import Thread

PORT = int(os.getenv("PORT", "8000"))
URL = f"http://localhost:{PORT}/control"
HEALTH_URL = f"http://localhost:{PORT}/health"

def check_and_setup_env():
    """Check if .env exists, if not copy from dot_env.example"""
    if not os.path.exists(".env"):
        if os.path.exists("dot_env.example"):
            print("📋 .env file not found, copying from dot_env.example...")
            try:
                shutil.copy("dot_env.example", ".env")
                print("✅ .env file created successfully!")
                print("💡 You can edit .env to customize your settings")
            except Exception as e:
                print(f"⚠️  Could not create .env file: {e}")
        else:
            print("⚠️  dot_env.example not found, .env file will not be created")

def is_setup_completed():
    """Check if setup has been completed by reading .env file"""
    if not os.path.exists(".env"):
        return False
    
    try:
        with open(".env", "r") as f:
            content = f.read()
            return "SETUP_COMPLETED=true" in content
    except:
        return False

def mark_setup_completed():
    """Mark setup as completed in .env file"""
    if not os.path.exists(".env"):
        return
    
    try:
        with open(".env", "r") as f:
            content = f.read()
        
        # Replace SETUP_COMPLETED=false with SETUP_COMPLETED=true
        if "SETUP_COMPLETED=false" in content:
            content = content.replace("SETUP_COMPLETED=false", "SETUP_COMPLETED=true")
        elif "SETUP_COMPLETED=" in content:
            # If the line exists but with a different value, update it
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith("SETUP_COMPLETED="):
                    lines[i] = "SETUP_COMPLETED=true"
                    break
            content = '\n'.join(lines)
        else:
            # If the line doesn't exist, add it
            content += "\nSETUP_COMPLETED=true"
        
        with open(".env", "w") as f:
            f.write(content)
        
        print("✅ Setup marked as completed")
    except Exception as e:
        print(f"⚠️  Could not update .env file: {e}")

def reset_setup_status():
    """Reset setup status to allow running setup guide again"""
    if not os.path.exists(".env"):
        return
    
    try:
        with open(".env", "r") as f:
            content = f.read()
        
        # Replace SETUP_COMPLETED=true with SETUP_COMPLETED=false
        if "SETUP_COMPLETED=true" in content:
            content = content.replace("SETUP_COMPLETED=true", "SETUP_COMPLETED=false")
            with open(".env", "w") as f:
                f.write(content)
            print("✅ Setup status reset - you can run setup guide again")
        else:
            print("ℹ️  Setup status is already false")
    except Exception as e:
        print(f"⚠️  Could not reset .env file: {e}")

def is_blackhole_installed():
    """Check if BlackHole is already installed on macOS"""
    if platform.system() != "Darwin":
        return False
    
    try:
        result = subprocess.run(["brew", "list", "blackhole-2ch"], 
                              capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False

def interactive_audio_setup():
    """Interactive audio setup guide for users"""
    print("\n" + "="*60)
    print("🎵 AUDIO SETUP GUIDE")
    print("="*60)
    print("Tekstemaskin needs proper audio configuration for best results.")
    print("This guide will help you set up audio capture for meetings.")
    
    system = platform.system()
    
    if system == "Darwin":  # macOS
        return audio_setup_macos()
    elif system == "Windows":
        return audio_setup_windows()
    elif system == "Linux":
        return audio_setup_linux()
    else:
        print(f"❌ Unsupported operating system: {system}")
        return False

def audio_setup_macos():
    """macOS audio setup guide"""
    print("\n🍎 macOS Audio Setup")
    print("For digital meetings, you'll want to capture both:")
    print("  • Your microphone (for your voice)")
    print("  • System audio (for other participants)")
    
    print("\n📋 Step-by-step setup:")
    print("1. Install BlackHole 2ch (if not already installed)")
    print("2. Open Audio MIDI Setup (Applications > Utilities)")
    print("3. Create a Multi-Output Device")
    print("4. Add your speakers/headphones + BlackHole 2ch")
    print("5. Set Multi-Output Device as system audio output")
    print("6. In Tekstemaskin, select 'BlackHole 2ch' as input")
    
    # Check if BlackHole is already installed
    if is_blackhole_installed():
        print("\n✅ BlackHole 2ch is already installed!")
        print("   You can skip the installation step.")
        return True
    
    # Check if BlackHole is installed
    print("\n🔍 Checking BlackHole installation...")
    try:
        result = subprocess.run(["brew", "list", "blackhole-2ch"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ BlackHole 2ch is installed via Homebrew")
            return True
        else:
            print("❌ BlackHole 2ch not found")
            print("   Install with: brew install blackhole-2ch")
    except:
        print("⚠️  Could not check BlackHole status")
    
    # Offer to install BlackHole
    print("\n🤔 Would you like to install BlackHole 2ch now? (y/n): ", end="")
    try:
        response = input().lower().strip()
        if response in ['y', 'yes', 'j', 'ja']:
            return install_blackhole_macos()
        else:
            print("⏭️  Skipping BlackHole installation.")
            print("   You can install it later with: brew install blackhole-2ch")
            return False
    except KeyboardInterrupt:
        print("\n⏭️  Installation cancelled.")
        return False

def install_blackhole_macos():
    """Install BlackHole on macOS"""
    print("\n🚀 Installing BlackHole 2ch...")
    
    try:
        # Check if Homebrew is installed
        result = subprocess.run(["brew", "--version"], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Homebrew is not installed. Please install Homebrew first:")
            print("   https://brew.sh")
            return False
        
        # Install BlackHole
        print("📦 Installing BlackHole 2ch via Homebrew...")
        result = subprocess.run(["brew", "install", "blackhole-2ch"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ BlackHole 2ch installed successfully!")
            print("\n📋 Next steps:")
            print("1. Open Audio MIDI Setup (Applications > Utilities)")
            print("2. Create a Multi-Output Device")
            print("3. Add your speakers + BlackHole 2ch")
            print("4. Set as system audio output")
            print("5. Restart your meeting applications")
            return True
        else:
            print(f"❌ BlackHole installation failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Installation error: {e}")
        return False

def audio_setup_windows():
    """Windows audio setup guide"""
    print("\n🪟 Windows Audio Setup")
    print("For digital meetings, you'll want to capture both:")
    print("  • Your microphone (for your voice)")
    print("  • System audio (for other participants)")
    
    print("\n📋 Step-by-step setup:")
    print("1. Enable Stereo Mix (if available)")
    print("   - Right-click speaker icon → Sound settings")
    print("   - Sound Control Panel → Recording tab")
    print("   - Right-click empty space → Show Disabled Devices")
    print("   - Right-click Stereo Mix → Enable")
    print("2. Or install VB-Audio Virtual Cable")
    print("3. In Tekstemaskin, select appropriate input device")
    
    # Check for Stereo Mix
    print("\n🔍 Checking audio devices...")
    try:
        result = subprocess.run(["powershell", "-Command", 
                               "Get-WmiObject -Class Win32_SoundDevice | Select-Object Name, Status"],
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Audio devices found")
            print("💡 Check Sound Control Panel for Stereo Mix")
        else:
            print("⚠️  Could not check audio devices")
    except:
        print("⚠️  Could not check audio devices")
    
    return True

def audio_setup_linux():
    """Linux audio setup guide"""
    print("\n🐧 Linux Audio Setup")
    print("For digital meetings, you'll want to capture both:")
    print("  • Your microphone (for your voice)")
    print("  • System audio (for other participants)")
    
    print("\n📋 Step-by-step setup:")
    print("1. Install PulseAudio (usually pre-installed)")
    print("2. Use pavucontrol to configure audio routing")
    print("3. Consider installing PulseAudio Volume Control")
    print("4. In Tekstemaskin, select appropriate input device")
    
    # Check PulseAudio
    print("\n🔍 Checking PulseAudio...")
    try:
        result = subprocess.run(["pulseaudio", "--version"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ PulseAudio found: {result.stdout.strip()}")
        else:
            print("❌ PulseAudio not found")
            print("   Install with: sudo apt install pulseaudio")
    except:
        print("⚠️  Could not check PulseAudio")
    
    return True

def check_ollama_installation():
    """Check if Ollama is installed and offer to install it"""
    print("🤖 Checking Ollama installation...")
    
    # Check if ollama command exists
    try:
        result = subprocess.run(["ollama", "--version"], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"✅ Ollama is installed: {result.stdout.strip()}")
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    # Check if Ollama service is running
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            print("✅ Ollama service is running")
            return True
    except:
        pass
    
    print("❌ Ollama is not installed or not running")
    return False

def offer_ollama_installation():
    """Offer to install Ollama for the user"""
    print("\n" + "="*60)
    print("🤖 OLLAMA INSTALLATION REQUIRED")
    print("="*60)
    print("Tekstemaskin needs Ollama for AI-powered meeting summaries.")
    print("Without Ollama, you can still transcribe but won't get summaries.")
    print("\nWould you like to install Ollama now? (y/n): ", end="")
    
    try:
        response = input().lower().strip()
        if response in ['y', 'yes', 'j', 'ja']:
            return install_ollama()
        else:
            print("⏭️  Skipping Ollama installation. You can install it later.")
            print("   See README.md for manual installation instructions.")
            return False
    except KeyboardInterrupt:
        print("\n⏭️  Installation cancelled.")
        return False

def install_ollama():
    """Install Ollama based on the operating system"""
    print("\n🚀 Installing Ollama...")
    
    system = sys.platform
    if system == "darwin":  # macOS
        return install_ollama_macos()
    elif system == "win32":  # Windows
        return install_ollama_windows()
    elif system.startswith("linux"):  # Linux
        return install_ollama_linux()
    else:
        print(f"❌ Unsupported operating system: {system}")
        print("   Please install Ollama manually from: https://ollama.ai")
        return False

def install_ollama_macos():
    """Install Ollama on macOS using Homebrew"""
    print("🍎 Installing Ollama on macOS...")
    
    try:
        # Check if Homebrew is installed
        result = subprocess.run(["brew", "--version"], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Homebrew is not installed. Please install Homebrew first:")
            print("   https://brew.sh")
            return False
        
        # Install Ollama
        print("📦 Installing Ollama via Homebrew...")
        result = subprocess.run(["brew", "install", "ollama"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Ollama installed successfully!")
            
            # Start Ollama service
            print("🚀 Starting Ollama service...")
            subprocess.Popen(["ollama", "serve"], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
            
            # Wait a bit for service to start
            time.sleep(3)
            
            # Pull a default model
            print("📥 Downloading default model (this may take a few minutes)...")
            result = subprocess.run(["ollama", "pull", "gpt-oss:20B"], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Default model downloaded successfully!")
                return True
            else:
                print("⚠️  Model download failed, but Ollama is installed.")
                print("   You can download models manually with: ollama pull <model>")
                return True
        else:
            print(f"❌ Ollama installation failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Installation error: {e}")
        return False

def install_ollama_windows():
    """Install Ollama on Windows using winget or manual download"""
    print("🪟 Installing Ollama on Windows...")
    
    try:
        # Try winget first
        result = subprocess.run(["winget", "install", "Ollama.Ollama"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Ollama installed successfully via winget!")
        else:
            print("📥 winget installation failed, downloading manually...")
            print("   Please download and install from: https://ollama.ai/download")
            print("   After installation, restart this script.")
            return False
        
        # Start Ollama service
        print("🚀 Starting Ollama service...")
        subprocess.Popen(["ollama", "serve"], 
                       stdout=subprocess.DEVNULL, 
                       stderr=subprocess.DEVNULL)
        
        time.sleep(3)
        
        # Pull default model
        print("📥 Downloading default model...")
        result = subprocess.run(["ollama", "pull", "gpt-oss:20B"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Default model downloaded successfully!")
            return True
        else:
            print("⚠️  Model download failed, but Ollama is installed.")
            return True
            
    except Exception as e:
        print(f"❌ Installation error: {e}")
        return False

def install_ollama_linux():
    """Install Ollama on Linux"""
    print("🐧 Installing Ollama on Linux...")
    
    try:
        # Use the official install script
        print("📥 Downloading Ollama install script...")
        result = subprocess.run([
            "curl", "-fsSL", "https://ollama.ai/install.sh"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("🚀 Running Ollama install script...")
            install_result = subprocess.run([
                "bash", "-c", result.stdout
            ], capture_output=True, text=True)
            
            if install_result.returncode == 0:
                print("✅ Ollama installed successfully!")
                
                # Start Ollama service
                print("🚀 Starting Ollama service...")
                subprocess.Popen(["ollama", "serve"], 
                               stdout=subprocess.DEVNULL, 
                               stderr=subprocess.DEVNULL)
                
                time.sleep(3)
                
                # Pull default model
                print("📥 Downloading default model...")
                model_result = subprocess.run(["ollama", "pull", "gpt-oss:20B"], 
                                           capture_output=True, text=True)
                
                if model_result.returncode == 0:
                    print("✅ Default model downloaded successfully!")
                    return True
                else:
                    print("⚠️  Model download failed, but Ollama is installed.")
                    return True
            else:
                print(f"❌ Ollama installation failed: {install_result.stderr}")
                return False
        else:
            print("❌ Could not download install script")
            return False
            
    except Exception as e:
        print(f"❌ Installation error: {e}")
        return False

def wait_for_server():
    """Wait for the server to be ready by checking the health endpoint"""
    max_attempts = 30  # Wait up to 30 seconds
    attempt = 0
    
    print("🔍 Checking if server is ready...")
    
    while attempt < max_attempts:
        try:
            response = requests.get(HEALTH_URL, timeout=1)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Server is ready! {data.get('status', '')}")
                return True
        except (requests.exceptions.RequestException, requests.exceptions.Timeout):
            pass
        
        attempt += 1
        time.sleep(1)
        if attempt % 5 == 0:  # Show progress every 5 seconds
            print(f"⏳ Waiting for server to start... ({attempt}s)")
    
    print("⚠️  Server startup timeout - browser will open anyway")
    return False

def open_browser():
    """Open browser after a short delay to ensure server is fully ready"""
    time.sleep(0.5)  # Small additional delay for safety
    try:
        webbrowser.open(URL)
        print(f"🌐 Browser opened: {URL}")
        print("🎉 Tekstemaskin is ready to use!")
    except Exception as e:
        print(f"⚠️  Could not open browser automatically: {e}")
        print(f"   Please open manually: {URL}")
        print("🎉 Tekstemaskin is ready to use!")

if __name__ == "__main__":
    # Check for command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--reset-setup":
            print("🔄 Resetting setup status...")
            reset_setup_status()
            sys.exit(0)
        elif sys.argv[1] == "--help":
            print("🚀 Tekstemaskin - Audio Transcription Tool")
            print("\nUsage:")
            print("  python -m app.__main__          # Start normally")
            print("  python -m app.__main__ --reset-setup  # Reset setup status")
            print("  python -m app.__main__ --help         # Show this help")
            sys.exit(0)
    
    print("🚀 Starting Tekstemaskin server...")
    
    # Step 1: Setup environment file
    check_and_setup_env()
    
    # Check if setup has already been completed
    if is_setup_completed():
        print("✅ Setup already completed - starting server directly...")
        print("\n" + "="*60)
        print("🚀 STARTING TEKSTEMASKIN SERVER")
        print("="*60)
    else:
        # Step 2: Interactive audio setup guide
        print("\n🎵 Audio Setup Guide")
        print("This will help you configure audio for digital meetings.")
        print("You can skip this and configure later if you prefer.")
        print("\nWould you like to run the audio setup guide? (y/n): ", end="")
        
        try:
            response = input().lower().strip()
            if response in ['y', 'yes', 'j', 'ja']:
                interactive_audio_setup()
            else:
                print("⏭️  Skipping audio setup guide.")
                print("   You can configure audio in the Tekstemaskin control panel")
        except KeyboardInterrupt:
            print("\n⏭️  Audio setup cancelled.")
        
        # Step 3: Check Ollama installation
        ollama_installed = check_ollama_installation()
        if not ollama_installed:
            ollama_installed = offer_ollama_installation()
        
        if ollama_installed:
            print("🤖 Ollama is ready for AI summaries!")
        else:
            print("⚠️  Ollama not available - summaries will not work")
            print("   You can still use transcription features")
        
        # Mark setup as completed
        mark_setup_completed()
        
        print("\n" + "="*60)
        print("🚀 STARTING TEKSTEMASKIN SERVER")
        print("="*60)
    
    # Start server in a separate thread
    server_thread = Thread(target=lambda: uvicorn.run(
        "app.main:app", 
        host="0.0.0.0", 
        port=PORT, 
        reload=False,
        log_level="info"
    ), daemon=True)
    
    server_thread.start()
    
    # Wait for server to be ready
    if wait_for_server():
        open_browser()
    else:
        # If health check fails, still try to open browser
        print("⚠️  Health check failed, but trying to open browser anyway...")
        time.sleep(2)  # Give a bit more time
        open_browser()
    
    # Keep main thread alive
    try:
        server_thread.join()
    except KeyboardInterrupt:
        print("\n👋 Shutting down Tekstemaskin...")