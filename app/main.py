from fastapi import FastAPI

from app.api.v1.router import api_router
from app.config import get_settings

app = FastAPI(
    title="SQL Agent",
    description="Natural language to SQL agent powered by DeepSeek",
    version="0.1.0",
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health() -> dict[str, str]:
    settings = get_settings()
    return {
        "status": "ok",
        "model": settings.deepseek_model,
        "database": str(settings.db_path),
    }
