import os
import webbrowser
import uvicorn
import time
import requests
from threading import Thread

PORT = int(os.getenv("PORT", "8000"))
URL = f"http://localhost:{PORT}/control"
HEALTH_URL = f"http://localhost:{PORT}/health"

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