"""High-level speech generation service."""

import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import numpy as np

from src.core.tts_engine import TTSEngine
from src.core.text_processor import TextProcessor
from src.core.audio_processor import AudioProcessor
from src.core.emotion_controller import EmotionController
from config.settings import Settings


@dataclass
class SynthesisResult:
    """Result of speech synthesis."""
    
    job_id: str
    audio_path: str
    audio_url: str
    duration: float
    model_name: str
    expires_at: Optional[datetime] = None


class SpeechService:
    """High-level service for speech generation."""

    def __init__(self, settings: Settings):
        """Initialize speech service.
        
        Args:
            settings: Application settings
        """
        self.settings = settings
        self.tts_engine = TTSEngine(settings)
        self.text_processor = TextProcessor(max_length=settings.max_text_length)
        self.audio_processor = AudioProcessor(sample_rate=settings.default_sample_rate)
        self.emotion_controller = EmotionController()
        
        # Ensure output directory exists
        Path(settings.audio_output_dir).mkdir(parents=True, exist_ok=True)

    async def synthesize(
        self,
        text: str,
        emotion: str = "neutral",
        intensity: float = 0.5,
        voice_id: str = "default_documentary",
        output_format: str = "wav",
        sample_rate: int = 24000,
        options: Optional[dict] = None
    ) -> SynthesisResult:
        """Synthesize emotional speech from text.
        
        Args:
            text: Input text to synthesize
            emotion: Emotion to apply
            intensity: Emotion intensity (0.0-1.0)
            voice_id: Voice identifier
            output_format: Output format (wav, mp3, ogg)
            sample_rate: Target sample rate
            options: Additional options (normalize_audio, remove_silence, speed)
            
        Returns:
            Synthesis result with audio path and metadata
        """
        # Generate job ID
        job_id = str(uuid.uuid4())
        
        # Parse options
        options = options or {}
        normalize_audio = options.get("normalize_audio", True)
        remove_silence = options.get("remove_silence", False)
        speed = options.get("speed", 1.0)
        
        try:
            # Step 1: Process text
            normalized_text = self.text_processor.normalize(text)
            
            # Step 2: Validate emotion
            if not self.emotion_controller.validate_emotion(emotion):
                available = list(self.emotion_controller.list_emotions().keys())
                raise ValueError(
                    f"Invalid emotion '{emotion}'. Available: {', '.join(available)}"
                )
            
            # Step 3: Synthesize speech
            audio = self.tts_engine.synthesize(
                text=normalized_text,
                emotion=emotion,
                intensity=intensity
            )
            
            # Step 4: Post-process audio
            audio = self.audio_processor.process_pipeline(
                audio=audio,
                normalize=normalize_audio,
                remove_silence=remove_silence,
                speed=speed
            )
            
            # Step 5: Save audio
            output_filename = f"{job_id}.{output_format}"
            output_path = Path(self.settings.audio_output_dir) / output_filename
            
            self.audio_processor.save_audio(
                audio=audio,
                output_path=output_path,
                sample_rate=sample_rate
            )
            
            # Step 6: Calculate metadata
            duration = len(audio) / sample_rate
            expires_at = datetime.now() + timedelta(hours=self.settings.audio_ttl_hours)
            
            # Generate URL (for production, use CDN)
            audio_url = f"/audio/{output_filename}"
            
            return SynthesisResult(
                job_id=job_id,
                audio_path=str(output_path),
                audio_url=audio_url,
                duration=duration,
                model_name=self.tts_engine.model.model_name if self.tts_engine.model else "unknown",
                expires_at=expires_at
            )
            
        except Exception as e:
            raise RuntimeError(f"Speech synthesis failed: {str(e)}") from e

    def list_emotions(self) -> dict:
        """Get available emotions with metadata.
        
        Returns:
            Dictionary of emotions and their configurations
        """
        emotions = self.emotion_controller.list_emotions()
        return {
            emotion_id: {
                "id": emotion_id,
                "name": config.name,
                "description": config.description,
                "recommended_intensity": config.recommended_intensity,
                "use_cases": config.use_cases
            }
            for emotion_id, config in emotions.items()
        }

    def get_model_info(self) -> dict:
        """Get information about the loaded model.
        
        Returns:
            Model information dictionary
        """
        if not self.tts_engine.model:
            return {"loaded": False}
        
        return {
            "loaded": self.tts_engine.model.is_loaded,
            "name": self.tts_engine.model.model_name,
            "device": self.tts_engine.model.device,
            "sample_rate": self.tts_engine.get_sample_rate(),
            "supported_emotions": self.tts_engine.get_supported_emotions()
        }

