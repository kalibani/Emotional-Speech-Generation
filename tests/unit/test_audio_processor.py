"""Unit tests for AudioProcessor."""

import pytest
import numpy as np
from src.core.audio_processor import AudioProcessor


class TestAudioProcessor:
    """Test suite for AudioProcessor."""
    
    def test_normalize_audio(self):
        """Test audio normalization."""
        processor = AudioProcessor()
        audio = np.random.randn(1000).astype(np.float32) * 0.1
        normalized = processor.normalize_audio(audio)
        assert normalized.max() <= 1.0
        assert normalized.min() >= -1.0
    
    def test_normalize_audio_prevents_clipping(self):
        """Test that normalization prevents clipping."""
        processor = AudioProcessor()
        audio = np.random.randn(1000).astype(np.float32) * 10  # Very loud
        normalized = processor.normalize_audio(audio)
        assert np.all(normalized <= 1.0)
        assert np.all(normalized >= -1.0)
    
    def test_remove_silence(self):
        """Test silence removal."""
        processor = AudioProcessor()
        # Create audio with silence
        audio = np.concatenate([
            np.random.randn(1000) * 0.5,  # Sound
            np.zeros(1000),  # Silence
            np.random.randn(1000) * 0.5  # Sound
        ]).astype(np.float32)
        
        result = processor.remove_silence(audio)
        assert len(result) < len(audio)
    
    def test_change_speed(self):
        """Test speed change."""
        processor = AudioProcessor()
        audio = np.random.randn(1000).astype(np.float32)
        
        # Speed up
        faster = processor.change_speed(audio, speed=1.5)
        assert len(faster) < len(audio)
        
        # Slow down
        slower = processor.change_speed(audio, speed=0.75)
        assert len(slower) > len(audio)
    
    def test_save_and_load_audio(self, tmp_path):
        """Test saving and loading audio."""
        processor = AudioProcessor()
        audio = np.random.randn(1000).astype(np.float32)
        
        # Save
        output_path = tmp_path / "test.wav"
        processor.save_audio(audio, output_path)
        assert output_path.exists()
        
        # Load
        loaded_audio, sample_rate = processor.load_audio(output_path)
        assert len(loaded_audio) > 0
        assert sample_rate == processor.sample_rate
    
    def test_process_pipeline(self):
        """Test complete processing pipeline."""
        processor = AudioProcessor()
        audio = np.random.randn(1000).astype(np.float32) * 0.1
        
        processed = processor.process_pipeline(
            audio,
            normalize=True,
            remove_silence=False,
            compress=False,
            speed=1.0
        )
        
        assert len(processed) > 0
        assert processed.max() <= 1.0
        assert processed.min() >= -1.0

