import os
import webbrowser
import uvicorn
import time
import requests
import shutil
import subprocess
import sys
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
    print("🚀 Starting Tekstemaskin server...")
    
    # Step 1: Setup environment file
    check_and_setup_env()
    
    # Step 2: Check Ollama installation
    ollama_installed = check_ollama_installation()
    if not ollama_installed:
        ollama_installed = offer_ollama_installation()
    
    if ollama_installed:
        print("🤖 Ollama is ready for AI summaries!")
    else:
        print("⚠️  Ollama not available - summaries will not work")
        print("   You can still use transcription features")
    
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