"""TTS engine abstraction layer."""

from typing import Optional, Dict, Any
import numpy as np

from src.models.base import BaseTTSModel
from src.models.coqui import CoquiTTSModel
from config.settings import Settings


class TTSEngine:
    """Main TTS engine that manages model loading and synthesis."""

    def __init__(self, settings: Settings):
        """Initialize TTS engine.
        
        Args:
            settings: Application settings
        """
        self.settings = settings
        self.model: Optional[BaseTTSModel] = None
        self._initialize_model()

    def _initialize_model(self) -> None:
        """Initialize the TTS model based on settings."""
        model_map = {
            "coqui": CoquiTTSModel,
            # "chatterbox": ChatterboxModel,  # Implement when available
            # "bark": BarkModel,  # Implement when available
        }

        model_class = model_map.get(self.settings.model_name)
        if not model_class:
            raise ValueError(
                f"Unknown model: {self.settings.model_name}. "
                f"Available: {', '.join(model_map.keys())}"
            )

        self.model = model_class(device=self.settings.device)

    def load_model(self) -> None:
        """Load the TTS model."""
        if self.model and not self.model.is_loaded:
            self.model.load_model()

    def synthesize(
        self,
        text: str,
        emotion: str = "neutral",
        intensity: float = 0.5,
        **kwargs: Any
    ) -> np.ndarray:
        """Synthesize speech from text.
        
        Args:
            text: Input text
            emotion: Emotion to apply
            intensity: Emotion intensity (0.0-1.0)
            **kwargs: Additional synthesis parameters
            
        Returns:
            Audio array as numpy
        """
        if not self.model:
            raise RuntimeError("No model initialized")

        if not self.model.is_loaded:
            self.load_model()

        # Validate emotion
        if not self.model.validate_emotion(emotion):
            raise ValueError(
                f"Emotion '{emotion}' not supported. "
                f"Available: {', '.join(self.model.get_supported_emotions())}"
            )

        # Synthesize
        audio = self.model.synthesize(
            text=text,
            emotion=emotion,
            intensity=intensity,
            **kwargs
        )

        return audio

    def get_sample_rate(self) -> int:
        """Get current model's sample rate.
        
        Returns:
            Sample rate in Hz
        """
        if not self.model:
            return self.settings.default_sample_rate
        return self.model.get_sample_rate()

    def get_supported_emotions(self) -> list[str]:
        """Get list of supported emotions.
        
        Returns:
            List of emotion identifiers
        """
        if not self.model:
            return []
        return self.model.get_supported_emotions()

    def unload_model(self) -> None:
        """Unload model to free memory."""
        if self.model:
            self.model.unload_model()

