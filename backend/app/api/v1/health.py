from fastapi import APIRouter
from app.core.config import settings
from app.core.database import get_active_db_type
from app.schemas.ai import HealthResponse

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("", response_model=HealthResponse)
async def health_check():
    active_model = settings.GEMINI_MODEL if (settings.LLM_PROVIDER == "gemini" and settings.GEMINI_API_KEY) else settings.OPENROUTER_MODEL
    return {
        "status": "healthy",
        "appName": settings.APP_NAME,
        "dbEngine": get_active_db_type(),
        "llmProvider": settings.LLM_PROVIDER,
        "llmModel": active_model,
        "vectorDimension": settings.VECTOR_DIMENSION,
        "geminiEmbeddingConfigured": bool(settings.GEMINI_API_KEY)
    }
