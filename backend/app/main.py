"""
VOTE-GUARD Backend API
FastAPI Application Entrypoint with modular routers, RBAC auth, 2FA KYC checks, and atomic verification.
Serves dedicated pages for Login & Signup, Operator Terminal, and Admin Portal.
"""

import os
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse

# Load .env file reliably using absolute paths regardless of current working directory
backend_dir = Path(__file__).resolve().parent.parent
backend_env = backend_dir / ".env"
root_env = backend_dir.parent / ".env"
frontend_dir = backend_dir.parent

if backend_env.exists():
    load_dotenv(dotenv_path=backend_env, override=True)
elif root_env.exists():
    load_dotenv(dotenv_path=root_env, override=True)
else:
    load_dotenv(override=True)

# Import database connection health-check
from app.database import check_db_connection

# Import modular routers
from app.routers.auth import router as auth_router
from app.routers.voting import router as voting_router
from app.routers.admin import router as admin_router

APP_NAME = os.getenv("APP_NAME", "VOTE-GUARD Verification API")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
APP_ENV = os.getenv("APP_ENV", "development")

# Initialize FastAPI Application
app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="Centralized Voter Verification, 2FA KYC Credential Guard & Duplicate Voting Prevention Backend",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Cross-Origin Resource Sharing (CORS) Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Modular Routers
app.include_router(auth_router)
app.include_router(voting_router)
app.include_router(admin_router)


# ================= FRONTEND PAGE ROUTING =================

@app.get("/")
def get_root_page():
    """Starting page: Serves Login & Signup page."""
    login_html = frontend_dir / "login.html"
    if not login_html.exists():
        login_html = frontend_dir / "index.html"
    return FileResponse(login_html)


@app.get("/index.html")
def get_index_page():
    """Serves index page."""
    idx_html = frontend_dir / "index.html"
    if idx_html.exists():
        return FileResponse(idx_html)
    return FileResponse(frontend_dir / "login.html")


@app.get("/login.html")
def get_login_page():
    """Serves Login & Signup page."""
    return FileResponse(frontend_dir / "login.html")


@app.get("/operator.html")
def get_operator_page():
    """Serves dedicated Operator Terminal page."""
    return FileResponse(frontend_dir / "operator.html")


@app.get("/admin.html")
def get_admin_page():
    """Serves dedicated Admin Security & Management Portal."""
    return FileResponse(frontend_dir / "admin.html")


@app.get("/portal")
def get_portal():
    """Redirects to root starting page."""
    return RedirectResponse(url="/")


@app.get("/style.css")
def get_style():
    """Serve frontend stylesheet."""
    return FileResponse(frontend_dir / "style.css", media_type="text/css")


@app.get("/auth.js")
def get_auth_js():
    return FileResponse(frontend_dir / "auth.js", media_type="application/javascript")


@app.get("/operator.js")
def get_operator_js():
    return FileResponse(frontend_dir / "operator.js", media_type="application/javascript")


@app.get("/admin.js")
def get_admin_js():
    return FileResponse(frontend_dir / "admin.js", media_type="application/javascript")


@app.get("/script.js")
def get_script_js():
    return FileResponse(frontend_dir / "script.js", media_type="application/javascript")


# ================= SYSTEM HEALTH =================

@app.get("/health")
def health_check():
    """
    Health check endpoint for operational diagnostics.
    Reports API service health and performs a live check on MySQL Server connectivity.
    """
    db_status = check_db_connection()

    return {
        "status": "healthy" if db_status.get("status") == "connected" else "degraded",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "vote-guard-backend",
        "version": APP_VERSION,
        "database": db_status,
    }


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")

    print(f"Starting {APP_NAME} v{APP_VERSION} on http://{host}:{port}")
    uvicorn.run("app.main:app", host=host, port=port, reload=debug)
