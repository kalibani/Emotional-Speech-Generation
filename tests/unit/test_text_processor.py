"""Unit tests for TextProcessor."""

import pytest
from src.core.text_processor import TextProcessor


class TestTextProcessor:
    """Test suite for TextProcessor."""
    
    def test_normalize_basic(self):
        """Test basic text normalization."""
        processor = TextProcessor()
        text = "  Hello   world  "
        result = processor.normalize(text)
        assert result == "Hello world"
    
    def test_normalize_empty_raises_error(self):
        """Test that empty text raises ValueError."""
        processor = TextProcessor()
        with pytest.raises(ValueError, match="Text cannot be empty"):
            processor.normalize("")
    
    def test_normalize_whitespace_only_raises_error(self):
        """Test that whitespace-only text raises ValueError."""
        processor = TextProcessor()
        with pytest.raises(ValueError, match="Text cannot be empty"):
            processor.normalize("   ")
    
    def test_normalize_too_long_raises_error(self):
        """Test that text exceeding max length raises ValueError."""
        processor = TextProcessor(max_length=10)
        long_text = "a" * 20
        with pytest.raises(ValueError, match="Text too long"):
            processor.normalize(long_text)
    
    def test_normalize_punctuation(self):
        """Test punctuation normalization."""
        processor = TextProcessor()
        text = "Hello,world!How are you?"
        result = processor.normalize(text)
        assert result == "Hello, world! How are you?"
    
    def test_expand_numbers(self):
        """Test number expansion."""
        processor = TextProcessor()
        text = "I have 2 apples and 5 oranges."
        result = processor.normalize(text)
        assert "two" in result.lower()
        assert "five" in result.lower()
    
    def test_chunk_text(self):
        """Test text chunking."""
        processor = TextProcessor()
        text = "First sentence. Second sentence. Third sentence."
        chunks = processor.chunk_text(text, max_chunk_size=30)
        assert len(chunks) > 1
        assert all(len(chunk) <= 35 for chunk in chunks)  # Small buffer
    
    def test_detect_emotion_excited(self):
        """Test emotion detection for excited text."""
        processor = TextProcessor()
        text = "This is an amazing discovery!"
        emotion = processor.detect_emotion_hints(text)
        assert emotion == "excited"
    
    def test_detect_emotion_sad(self):
        """Test emotion detection for sad text."""
        processor = TextProcessor()
        text = "Unfortunately, there was a tragic loss."
        emotion = processor.detect_emotion_hints(text)
        assert emotion == "sad"
    
    def test_detect_emotion_neutral(self):
        """Test emotion detection for neutral text."""
        processor = TextProcessor()
        text = "The weather is normal today."
        emotion = processor.detect_emotion_hints(text)
        assert emotion == "neutral"

