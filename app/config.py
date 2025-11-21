"""
Configuration management with strict type safety.

All configuration is loaded from environment variables and validated
at application startup using Pydantic.
"""

from functools import lru_cache
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from app.types import LogLevel, UserID


class Settings(BaseSettings):
    """Application settings with validation."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
        frozen=True,
    )
    
    # Application
    APP_NAME: str = "AI Social Media System"
    DEBUG: bool = False
    LOG_LEVEL: LogLevel = "INFO"
    
    # Telegram
    TELEGRAM_BOT_TOKEN: str = Field(default="test_token:test", min_length=10)
    TELEGRAM_ALLOWED_USER_IDS: str = ""
    
    # OpenAI
    OPENAI_API_KEY: str = Field(default="test_key_12345678901234567890", min_length=20)
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    OPENAI_TEMPERATURE: float = Field(default=0.7, ge=0.0, le=2.0)
    OPENAI_MAX_TOKENS: int = Field(default=800, ge=1, le=4000)
    
    # Anthropic (optional backup)
    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-3-sonnet-20240229"
    
    # Google Drive (optional)
    GOOGLE_DRIVE_CREDENTIALS_JSON: str = ""
    GOOGLE_DRIVE_FOLDER_ID: str = ""
    
    # imageBB (required for image editing)
    IMAGEBB_API_KEY: str = ""
    
    # Replicate (required for image editing)
    REPLICATE_API_TOKEN: str = ""
    
    # Database
    DATABASE_URL: str = "sqlite:///./ai_social_system.db"
    
    # Redis (optional)
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Security & Performance
    MAX_IMAGE_SIZE_MB: int = Field(default=10, ge=1, le=50)
    REQUEST_TIMEOUT_SECONDS: int = Field(default=300, ge=30, le=600)
    MAX_CONVERSATION_HISTORY: int = Field(default=10, ge=1, le=50)
    
    @field_validator("TELEGRAM_BOT_TOKEN")
    @classmethod
    def validate_telegram_token(cls, v: str) -> str:
        """Validate Telegram bot token format."""
        if ":" not in v:
            raise ValueError("Invalid Telegram bot token format (must contain ':')")
        return v
    
    @property
    def allowed_user_ids(self) -> list[UserID]:
        """Parse and return list of allowed user IDs."""
        if not self.TELEGRAM_ALLOWED_USER_IDS.strip():
            return []
        
        try:
            return [
                int(uid.strip())
                for uid in self.TELEGRAM_ALLOWED_USER_IDS.split(",")
                if uid.strip()
            ]
        except ValueError as e:
            raise ValueError(f"Invalid user ID in TELEGRAM_ALLOWED_USER_IDS: {e}")
    
    @property
    def is_user_whitelist_enabled(self) -> bool:
        """Check if user whitelist is active."""
        return len(self.allowed_user_ids) > 0
    
    @property
    def is_image_editing_enabled(self) -> bool:
        """Check if image editing is configured."""
        return bool(self.IMAGEBB_API_KEY and self.REPLICATE_API_TOKEN)
    
    @property
    def is_google_drive_enabled(self) -> bool:
        """Check if Google Drive integration is configured."""
        return bool(self.GOOGLE_DRIVE_CREDENTIALS_JSON)


@lru_cache
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Using lru_cache ensures settings are loaded only once.
    """
    return Settings()
