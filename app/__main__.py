import os
import webbrowser
import uvicorn

PORT = int(os.getenv("PORT", "8000"))
URL = f"http://localhost:{PORT}/control"

try:
    webbrowser.open(URL)
except Exception:
    pass

uvicorn.run("app.main:app", host="0.0.0.0", port=PORT, reload=False)