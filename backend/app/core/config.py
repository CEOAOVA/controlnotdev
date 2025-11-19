"""
ControlNot v2 - Configuración
Gestión centralizada de configuración con Pydantic Settings
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional
import json


class Settings(BaseSettings):
    """Configuración de la aplicación"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    # ==========================================
    # APP CONFIG
    # ==========================================
    ENVIRONMENT: str = "development"
    APP_URL: str = "http://localhost:3000"
    API_V1_PREFIX: str = "/api/v1"

    # ==========================================
    # CORS
    # ==========================================
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",  # Vite dev server
    ]

    # ==========================================
    # OPENAI (Fallback)
    # ==========================================
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4o"
    OPENAI_MAX_TOKENS: int = 4000
    OPENAI_TEMPERATURE: float = 0.1

    # ==========================================
    # OPENROUTER (Multi-provider - Principal)
    # ==========================================
    OPENROUTER_API_KEY: Optional[str] = None
    OPENROUTER_MODEL: str = "openai/gpt-4o"
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"

    # ==========================================
    # GOOGLE CLOUD VISION (OCR)
    # ==========================================
    GOOGLE_CREDENTIALS_JSON: str

    @property
    def google_credentials_dict(self) -> dict:
        """Parse Google credentials from JSON string"""
        try:
            return json.loads(self.GOOGLE_CREDENTIALS_JSON)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid GOOGLE_CREDENTIALS_JSON: {e}")

    # ==========================================
    # GOOGLE DRIVE (Opcional)
    # ==========================================
    GOOGLE_DRIVE_FOLDER_ID: Optional[str] = None

    # ==========================================
    # EMAIL (SMTP Gmail)
    # ==========================================
    SMTP_EMAIL: str
    SMTP_PASSWORD: str
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587

    # ==========================================
    # STORAGE (Local - MVP)
    # ==========================================
    UPLOAD_DIR: str = "uploads"
    OUTPUT_DIR: str = "outputs"
    DATA_DIR: str = "data"
    TEMPLATES_DIR: str = "templates"

    # ==========================================
    # PROCESSING
    # ==========================================
    MAX_CONCURRENT_OCR: int = 5  # Parallel OCR tasks
    MAX_FILE_SIZE_MB: int = 10

    # ==========================================
    # AI PROVIDER STRATEGY
    # ==========================================
    @property
    def use_openrouter(self) -> bool:
        """Check if OpenRouter should be used"""
        return bool(self.OPENROUTER_API_KEY)

    @property
    def active_ai_provider(self) -> str:
        """Get active AI provider name"""
        return "OpenRouter" if self.use_openrouter else "OpenAI"

    @property
    def active_model(self) -> str:
        """Get active model name"""
        return self.OPENROUTER_MODEL if self.use_openrouter else self.OPENAI_MODEL


# Singleton settings instance
settings = Settings()
