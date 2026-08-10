# -*- coding: utf-8 -*-
"""
Moxra - FastAPI Application (Public)
"""

import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn

from ..core.config import Config
from .routes import router


def create_app(config: Config = None) -> FastAPI:
    """
    Create FastAPI application with all routes and middleware
    
    Args:
        config: Configuration object, uses Config.from_env() if None
    
    Returns:
        FastAPI application instance
    """
    config = config or Config.from_env()
    
    # Disable automatic documentation
    app = FastAPI(
        title="Moxra",
        description="Professional NSFW content detection API - Public Access",
        version="1.0.0",
        docs_url=None,
        redoc_url=None,
        openapi_url=None
    )
    
    # CORS settings - Allow all domains for public API
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Static files setup
    base_dir = Path(__file__).parent.parent.parent
    
    static_dir = base_dir / "static"
    templates_dir = base_dir / "templates"
    
    static_dir.mkdir(parents=True, exist_ok=True)
    templates_dir.mkdir(parents=True, exist_ok=True)
    
    img_dir = static_dir / "img"
    img_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"📁 Static files path: {static_dir}")
    print(f"📁 Templates path: {templates_dir}")
    print(f"📁 Images path: {img_dir}")
    
    # Mount static files
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    
    # Add API routes
    app.include_router(router)
    
    # Main route with web interface
    @app.get("/")
    async def root(request: Request):
        """Display main web interface"""
        # Read HTML file directly
        html_path = templates_dir / "index.html"
        if html_path.exists():
            with open(html_path, "r", encoding="utf-8") as f:
                html_content = f.read()
            return HTMLResponse(content=html_content)
        else:
            return HTMLResponse(content="<h1>Template not found</h1>", status_code=404)
    
    return app


def run_server(config: Config = None):
    """
    Run FastAPI server
    
    Args:
        config: Configuration object
    """
    config = config or Config.from_env()
    app = create_app(config)
    
    print("=" * 60)
    print("🚀 Moxra - NSFW Content Detection (Public API)")
    print("=" * 60)
    print(f"🌐 Web Interface: http://localhost:{config.port}")
    print(f"🏥 Health Check: http://localhost:{config.port}/api/v1/health")
    print("=" * 60)
    print("📤 POST /api/v1/classify-img    - Upload image (JPG, PNG, WEBP, BMP)")
    print("🎞️ POST /api/v1/classify-gif    - Upload GIF animation")
    print("🎬 POST /api/v1/classify-video  - Upload video (MP4, AVI, MOV, MKV)")
    print("🔗 POST /api/v1/classify-url    - Analyze via URL")
    print("🧹 POST /api/v1/cleanup         - Memory cleanup")
    print("=" * 60)
    print("🔓 Public API - No authentication required")
    print("=" * 60)
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=config.port,
        log_level="info" if config.debug else "warning"
    )


if __name__ == "__main__":
    run_server()