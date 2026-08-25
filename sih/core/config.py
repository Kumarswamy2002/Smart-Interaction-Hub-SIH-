from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    PROJECT_NAME: str = "Smart Interaction Hub"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Environment
    ENV: str = Field(default="development")
    DEBUG: bool = Field(default=True)
    
    # Security
    SECRET_KEY: str = Field(default="sih-super-secret-production-grade-key-2026-08-25")
    ENCRYPTION_KEY: str = Field(default="gAAAAABm-sih-fernet-secret-key-32bytes-base64=")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    
    # Storage & DB
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    DATA_DIR: Path = BASE_DIR / ".sih_data"
    DATABASE_URL: str = f"sqlite+aiosqlite:///{DATA_DIR}/sih.db"
    
    # LLM / Intelligence Provider Config
    DEFAULT_LLM_PROVIDER: str = "mock"  # Options: mock, openai, anthropic, ollama
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    
    model_config = {
        "env_file": ".env",
        "extra": "ignore"
    }

settings = Settings()
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
