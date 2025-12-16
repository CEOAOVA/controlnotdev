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
        "https://pruebas.aurinot.com",  # Produccion
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
    # ANTHROPIC (Semana 1 - Quick Wins)
    # ==========================================
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-3-5-sonnet-20241022"
    ANTHROPIC_MAX_TOKENS: int = 4096
    ANTHROPIC_TEMPERATURE: float = 0.3

    # ==========================================
    # REDIS (Caching - Semana 1)
    # ==========================================
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_PASSWORD: Optional[str] = None
    REDIS_TTL: int = 300  # 5 minutos
    REDIS_MAX_CONNECTIONS: int = 10

    # ==========================================
    # SUPABASE (Database + Storage + Auth)
    # ==========================================
    SUPABASE_URL: str
    SUPABASE_KEY: str  # anon/public key
    SUPABASE_JWT_SECRET: Optional[str] = None  # for JWT verification
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = None  # for admin operations

    # ==========================================
    # GOOGLE CLOUD VISION (OCR)
    # ==========================================
    GOOGLE_CREDENTIALS_JSON: str

    @property
    def google_credentials_dict(self) -> dict:
        """Parse Google credentials from JSON string"""
        try:
            # Limpiar el JSON de posibles envolturas de Coolify/Docker
            json_str = self.GOOGLE_CREDENTIALS_JSON.strip()

            # Quitar comillas simples o dobles envolventes
            if (json_str.startswith("'") and json_str.endswith("'")) or \
               (json_str.startswith('"') and json_str.endswith('"')):
                json_str = json_str[1:-1]

            # Quitar escapes de comillas si existen
            json_str = json_str.replace('\\"', '"')

            return json.loads(json_str)
        except json.JSONDecodeError as e:
            # Log para debugging
            import structlog
            logger = structlog.get_logger()
            logger.error(
                "Error parsing GOOGLE_CREDENTIALS_JSON",
                raw_value_start=self.GOOGLE_CREDENTIALS_JSON[:50] if self.GOOGLE_CREDENTIALS_JSON else "EMPTY",
                error=str(e)
            )
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
    LOCAL_STORAGE_PATH: str = "storage"

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
_settings: Optional[Settings] = None

def get_settings() -> Settings:
    """Get or create settings singleton"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

# For backwards compatibility
settings = get_settings()
