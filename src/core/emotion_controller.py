"""Emotion control for TTS synthesis."""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any

import yaml


@dataclass
class EmotionConfig:
    """Configuration for a specific emotion."""
    
    name: str
    description: str
    recommended_intensity: float
    use_cases: list[str]
    prosody: Dict[str, float]


class EmotionController:
    """Control emotional parameters for TTS synthesis."""

    def __init__(self, config_path: str = "config/emotions.yaml"):
        """Initialize emotion controller.
        
        Args:
            config_path: Path to emotions configuration file
        """
        self.emotions: Dict[str, EmotionConfig] = {}
        self._load_emotions(config_path)

    def _load_emotions(self, config_path: str) -> None:
        """Load emotion configurations from YAML file.
        
        Args:
            config_path: Path to configuration file
        """
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                
            for emotion_id, emotion_data in config.get('emotions', {}).items():
                self.emotions[emotion_id] = EmotionConfig(
                    name=emotion_data['name'],
                    description=emotion_data['description'],
                    recommended_intensity=emotion_data['recommended_intensity'],
                    use_cases=emotion_data['use_cases'],
                    prosody=emotion_data['prosody']
                )
        except FileNotFoundError:
            # Fallback to default emotions if config not found
            self._load_default_emotions()

    def _load_default_emotions(self) -> None:
        """Load default emotion configurations."""
        self.emotions = {
            'neutral': EmotionConfig(
                name='Neutral',
                description='Standard documentary narration',
                recommended_intensity=0.5,
                use_cases=['facts', 'introductions'],
                prosody={'pitch_scale': 1.0, 'energy_scale': 1.0, 'tempo_scale': 1.0}
            ),
            'excited': EmotionConfig(
                name='Excited',
                description='Enthusiastic discovery',
                recommended_intensity=0.7,
                use_cases=['discoveries', 'revelations'],
                prosody={'pitch_scale': 1.15, 'energy_scale': 1.25, 'tempo_scale': 1.1}
            ),
            'sad': EmotionConfig(
                name='Sad',
                description='Somber tone',
                recommended_intensity=0.6,
                use_cases=['tragic events', 'loss'],
                prosody={'pitch_scale': 0.90, 'energy_scale': 0.75, 'tempo_scale': 0.85}
            ),
            'serious': EmotionConfig(
                name='Serious',
                description='Grave and authoritative',
                recommended_intensity=0.6,
                use_cases=['critical information', 'warnings'],
                prosody={'pitch_scale': 0.95, 'energy_scale': 1.1, 'tempo_scale': 0.9}
            ),
            'empathetic': EmotionConfig(
                name='Empathetic',
                description='Warm and understanding',
                recommended_intensity=0.65,
                use_cases=['human stories', 'emotional moments'],
                prosody={'pitch_scale': 1.0, 'energy_scale': 0.9, 'tempo_scale': 0.95}
            ),
        }

    def get_emotion(self, emotion_id: str) -> EmotionConfig:
        """Get emotion configuration.
        
        Args:
            emotion_id: Emotion identifier
            
        Returns:
            Emotion configuration
            
        Raises:
            ValueError: If emotion not found
        """
        if emotion_id not in self.emotions:
            available = ', '.join(self.emotions.keys())
            raise ValueError(
                f"Emotion '{emotion_id}' not found. "
                f"Available emotions: {available}"
            )
        return self.emotions[emotion_id]

    def list_emotions(self) -> Dict[str, EmotionConfig]:
        """Get all available emotions.
        
        Returns:
            Dictionary of emotion configurations
        """
        return self.emotions.copy()

    def apply_emotion_parameters(
        self, 
        emotion_id: str, 
        intensity: float = 0.5
    ) -> Dict[str, float]:
        """Calculate prosody parameters for given emotion and intensity.
        
        Args:
            emotion_id: Emotion identifier
            intensity: Emotion intensity (0.0-1.0)
            
        Returns:
            Dictionary of prosody parameters
            
        Raises:
            ValueError: If intensity out of range
        """
        if not 0.0 <= intensity <= 1.0:
            raise ValueError(f"Intensity must be between 0.0 and 1.0, got {intensity}")

        emotion = self.get_emotion(emotion_id)
        
        # Interpolate between neutral (1.0) and emotion values
        params = {}
        for key, emotion_value in emotion.prosody.items():
            # intensity=0 -> neutral (1.0), intensity=1 -> full emotion value
            params[key] = 1.0 + intensity * (emotion_value - 1.0)
        
        return params

    def validate_emotion(self, emotion_id: str) -> bool:
        """Check if emotion is valid.
        
        Args:
            emotion_id: Emotion identifier
            
        Returns:
            True if valid, False otherwise
        """
        return emotion_id in self.emotions

