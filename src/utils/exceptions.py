"""Custom exception classes."""


class TTSException(Exception):
    """Base exception for TTS-related errors."""
    pass


class ModelNotLoadedException(TTSException):
    """Raised when attempting to use an unloaded model."""
    pass


class UnsupportedEmotionException(TTSException):
    """Raised when an unsupported emotion is requested."""
    pass


class TextProcessingException(TTSException):
    """Raised when text processing fails."""
    pass


class AudioProcessingException(TTSException):
    """Raised when audio processing fails."""
    pass


class ValidationError(TTSException):
    """Raised when validation fails."""
    pass


class RateLimitException(TTSException):
    """Raised when rate limit is exceeded."""
    pass

