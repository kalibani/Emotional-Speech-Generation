"""TTS request and response schemas."""

from datetime import datetime
from typing import Optional, Literal

from pydantic import BaseModel, Field, field_validator


class SynthesisOptions(BaseModel):
    """Options for speech synthesis."""
    
    normalize_audio: bool = Field(default=True, description="Normalize audio levels")
    remove_silence: bool = Field(default=False, description="Remove long silences")
    speed: float = Field(default=1.0, ge=0.5, le=2.0, description="Playback speed multiplier")


class SynthesizeRequest(BaseModel):
    """Request schema for speech synthesis."""
    
    text: str = Field(..., min_length=1, max_length=5000, description="Text to synthesize")
    emotion: str = Field(default="neutral", description="Emotion to apply")
    intensity: float = Field(default=0.5, ge=0.0, le=1.0, description="Emotion intensity")
    voice_id: str = Field(default="default_documentary", description="Voice preset identifier")
    output_format: Literal["wav", "mp3", "ogg"] = Field(default="wav", description="Audio format")
    sample_rate: Literal[16000, 22050, 24000, 44100] = Field(default=24000, description="Sample rate in Hz")
    options: Optional[SynthesisOptions] = Field(default=None, description="Additional synthesis options")
    
    @field_validator("emotion")
    @classmethod
    def validate_emotion(cls, v: str) -> str:
        """Validate emotion value."""
        allowed = ["neutral", "excited", "sad", "serious", "empathetic", "urgent"]
        if v not in allowed:
            raise ValueError(f"Emotion must be one of {allowed}")
        return v
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "text": "Welcome to this fascinating documentary about the cosmos.",
                    "emotion": "excited",
                    "intensity": 0.7,
                    "voice_id": "default_documentary",
                    "output_format": "wav",
                    "sample_rate": 24000,
                    "options": {
                        "normalize_audio": True,
                        "remove_silence": False,
                        "speed": 1.0
                    }
                }
            ]
        }
    }


class SynthesisMetadata(BaseModel):
    """Metadata about the synthesis process."""
    
    text_length: int = Field(..., description="Length of input text")
    emotion_applied: str = Field(..., description="Emotion that was applied")
    intensity: float = Field(..., description="Intensity that was used")
    processing_time_ms: int = Field(..., description="Processing time in milliseconds")
    model: str = Field(..., description="Model name used")


class SynthesizeResponse(BaseModel):
    """Response schema for speech synthesis."""
    
    job_id: str = Field(..., description="Unique job identifier")
    status: Literal["completed", "processing", "failed"] = Field(..., description="Synthesis status")
    audio_url: Optional[str] = Field(None, description="URL to download audio")
    audio_base64: Optional[str] = Field(None, description="Base64-encoded audio (for small files)")
    duration_seconds: Optional[float] = Field(None, description="Audio duration in seconds")
    metadata: SynthesisMetadata = Field(..., description="Synthesis metadata")
    expires_at: Optional[datetime] = Field(None, description="Audio URL expiration time")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "job_id": "123e4567-e89b-12d3-a456-426614174000",
                    "status": "completed",
                    "audio_url": "/audio/123e4567-e89b-12d3-a456-426614174000.wav",
                    "duration_seconds": 8.3,
                    "metadata": {
                        "text_length": 62,
                        "emotion_applied": "excited",
                        "intensity": 0.7,
                        "processing_time_ms": 1247,
                        "model": "coqui"
                    },
                    "expires_at": "2025-10-31T12:00:00Z"
                }
            ]
        }
    }

