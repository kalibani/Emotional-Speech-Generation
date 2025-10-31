"""Pytest configuration and fixtures."""

import pytest
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import Settings


@pytest.fixture
def settings():
    """Provide test settings."""
    return Settings(
        debug=True,
        model_name="coqui",
        device="cpu",
        max_text_length=1000,
        audio_output_dir="data/test_audio",
        log_level="DEBUG"
    )


@pytest.fixture
def sample_text():
    """Provide sample text for testing."""
    return "This is a test of the emotional speech generation system."


@pytest.fixture
def temp_audio_file(tmp_path):
    """Provide temporary audio file path."""
    return tmp_path / "test_output.wav"

