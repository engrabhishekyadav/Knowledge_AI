import os
import json
from typing import List, Union
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator

class Settings(BaseSettings):
    APP_NAME: str = "KnowledgeAI Backend"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    
    # AI Settings
    LLM_PROVIDER: str = "gemini"
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-3.5-flash"
    GEMINI_FALLBACK_MODEL: str = "gemini-3.6-flash"
    GEMINI_BASE_URL: str = "https://generativelanguage.googleapis.com/v1beta/openai"

    OPENROUTER_API_KEY: str = ""
    OPENROUTER_MODEL: str = "minimax/minimax-m3:free"
    OPENROUTER_FALLBACK_MODEL: str = "nvidia/nemotron-3.5-lightning:free"
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    
    # Security & Auth Settings
    JWT_SECRET_KEY: str = ""
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    MAX_UPLOAD_SIZE_BYTES: int = 15 * 1024 * 1024  # 15 MB

    # Database Settings (PostgreSQL with pgvector)
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgre123@localhost:5433/knowledge_ai"
    
    # Vector Search & Embeddings
    GEMINI_EMBEDDING_MODEL: str = "gemini-embedding-001"
    VECTOR_DIMENSION: int = 768
    HYBRID_DEFAULT_WEIGHT: float = 0.65
    
    # CORS
    CORS_ORIGINS: Union[List[str], str] = ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"]

    @field_validator("JWT_SECRET_KEY", mode="before")
    @classmethod
    def validate_jwt_secret_key(cls, v):
        insecure_placeholder = "knowledge_ai_production_jwt_secret_key_2026_super_secure"
        if not v or v == insecure_placeholder or v == "replace_with_a_secure_random_secret_in_production":
            import secrets
            import logging
            generated = secrets.token_hex(32)
            logging.getLogger("knowledge_ai.config").warning(
                "JWT_SECRET_KEY not set or using insecure placeholder. "
                "Generated an ephemeral 256-bit key for this session. "
                "Set JWT_SECRET_KEY in backend/.env for production."
            )
            return generated
        return v

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except Exception:
                return [i.strip() for i in v.split(",")]
        return v

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
