"""Unit tests for EmotionController."""

import pytest
from src.core.emotion_controller import EmotionController


class TestEmotionController:
    """Test suite for EmotionController."""
    
    def test_load_default_emotions(self):
        """Test loading default emotions."""
        controller = EmotionController(config_path="nonexistent.yaml")
        emotions = controller.list_emotions()
        assert "neutral" in emotions
        assert "excited" in emotions
        assert "sad" in emotions
    
    def test_get_emotion(self):
        """Test getting emotion configuration."""
        controller = EmotionController()
        emotion = controller.get_emotion("excited")
        assert emotion.name == "Excited"
        assert emotion.recommended_intensity > 0
    
    def test_get_invalid_emotion_raises_error(self):
        """Test that invalid emotion raises ValueError."""
        controller = EmotionController()
        with pytest.raises(ValueError, match="not found"):
            controller.get_emotion("invalid_emotion")
    
    def test_validate_emotion(self):
        """Test emotion validation."""
        controller = EmotionController()
        assert controller.validate_emotion("neutral") is True
        assert controller.validate_emotion("invalid") is False
    
    def test_apply_emotion_parameters(self):
        """Test applying emotion parameters."""
        controller = EmotionController()
        params = controller.apply_emotion_parameters("excited", intensity=0.7)
        assert "pitch_scale" in params
        assert "energy_scale" in params
        assert "tempo_scale" in params
        assert params["pitch_scale"] != 1.0  # Should be modified
    
    def test_apply_emotion_neutral_intensity(self):
        """Test that zero intensity returns neutral parameters."""
        controller = EmotionController()
        params = controller.apply_emotion_parameters("excited", intensity=0.0)
        assert params["pitch_scale"] == 1.0
        assert params["energy_scale"] == 1.0
        assert params["tempo_scale"] == 1.0
    
    def test_invalid_intensity_raises_error(self):
        """Test that invalid intensity raises ValueError."""
        controller = EmotionController()
        with pytest.raises(ValueError, match="Intensity must be between"):
            controller.apply_emotion_parameters("neutral", intensity=1.5)
        with pytest.raises(ValueError, match="Intensity must be between"):
            controller.apply_emotion_parameters("neutral", intensity=-0.1)

