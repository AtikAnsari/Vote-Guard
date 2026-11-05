"""
VOTE-GUARD — Root Server Launcher
Runs the FastAPI server from the project root.
"""

import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.main import app

if __name__ == "__main__":
    import os
    import uvicorn

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    print(f"Starting VOTE-GUARD FastAPI server on http://{host}:{port} (LAN & Localhost accessible)")
    uvicorn.run("app.main:app", host=host, port=port, reload=True, app_dir=str(backend_dir))

