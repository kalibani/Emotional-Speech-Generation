"""Application settings using Pydantic for environment-based configuration."""

from functools import lru_cache
from typing import List, Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # Application
    app_name: str = Field(default="Emotional Speech Generation API")
    app_version: str = Field(default="1.0.0")
    debug: bool = Field(default=False)
    environment: Literal["development", "staging", "production"] = Field(default="development")

    # API
    api_v1_prefix: str = Field(default="/v1")
    cors_origins: List[str] = Field(default=["*"])
    api_key: str | None = Field(default=None)

    # TTS Model
    model_name: Literal["chatterbox", "coqui", "bark"] = Field(default="chatterbox")
    model_cache_dir: str = Field(default="data/models")
    device: Literal["cuda", "cpu", "mps"] = Field(default="cpu")

    # Audio Settings
    default_sample_rate: int = Field(default=24000)
    max_text_length: int = Field(default=5000)
    audio_output_dir: str = Field(default="data/audio_cache")
    audio_ttl_hours: int = Field(default=24)

    # Rate Limiting
    rate_limit_requests: int = Field(default=10)
    rate_limit_window: int = Field(default=60)

    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(default="INFO")

    # Storage (Optional - for S3)
    aws_access_key_id: str | None = Field(default=None)
    aws_secret_access_key: str | None = Field(default=None)
    aws_region: str = Field(default="us-east-1")
    s3_bucket: str | None = Field(default=None)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | List[str]) -> List[str]:
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

