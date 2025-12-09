"""Application configuration management."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Claude API
    anthropic_api_key: str = ""

    # Tesseract OCR
    tesseract_cmd: str = "tesseract"  # Default: assume in PATH

    # Storage
    storage_root: Path = Path("./storage")

    # Server
    host: str = "localhost"
    port: int = 8000

    # Debug
    debug: bool = False

    # CORS
    cors_origins: list[str] = ["*"]  # Allow all origins by default for local development


# Global settings instance
settings = Settings()
