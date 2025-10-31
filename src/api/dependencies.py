"""Dependency injection for FastAPI."""

from functools import lru_cache

from config.settings import Settings, get_settings
from src.services.speech_service import SpeechService


@lru_cache
def get_speech_service() -> SpeechService:
    """Get cached speech service instance.
    
    Returns:
        SpeechService instance
    """
    settings = get_settings()
    return SpeechService(settings)


def rate_limit() -> None:
    """Rate limiting dependency (placeholder).
    
    In production, implement proper rate limiting using:
    - slowapi library
    - Redis-based rate limiting
    - API gateway (AWS, Kong, etc.)
    """
    # TODO: Implement actual rate limiting
    pass

