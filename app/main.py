from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import api_router
from app.config import get_settings

STATIC_DIR = Path(__file__).resolve().parent / "static"

app = FastAPI(
    title="SQL Agent",
    description="Natural language to SQL agent powered by DeepSeek",
    version="0.1.0",
)

app.include_router(api_router, prefix="/api/v1")

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
async def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
async def health() -> dict[str, str]:
    settings = get_settings()
    return {
        "status": "ok",
        "model": settings.deepseek_model,
        "database": str(settings.db_path),
    }
