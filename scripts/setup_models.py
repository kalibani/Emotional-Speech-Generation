#!/usr/bin/env python3
"""Setup script to download and initialize TTS models."""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import Settings


def setup_directories() -> None:
    """Create necessary directories."""
    print("Creating directories...")
    
    settings = Settings()
    
    directories = [
        Path(settings.model_cache_dir),
        Path(settings.audio_output_dir),
        Path("data/logs")
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"  ✓ {directory}")


def download_models() -> None:
    """Download TTS models."""
    print("\nDownloading TTS models...")
    print("This may take a few minutes on first run...\n")
    
    try:
        from TTS.api import TTS
        
        settings = Settings()
        
        # Download the model
        print(f"Downloading model for {settings.model_name}...")
        
        if settings.model_name == "coqui":
            model_name = "tts_models/en/ljspeech/tacotron2-DDC"
            tts = TTS(model_name).to(settings.device)
            print(f"  ✓ Model downloaded: {model_name}")
        
        print("\n✓ All models downloaded successfully!")
        
    except ImportError:
        print("Error: Coqui TTS not installed")
        print("Install with: pip install TTS")
        sys.exit(1)
    except Exception as e:
        print(f"Error downloading models: {e}")
        sys.exit(1)


def test_synthesis() -> None:
    """Test synthesis with a simple example."""
    print("\nTesting synthesis...")
    
    try:
        from src.services.speech_service import SpeechService
        from config.settings import Settings
        import asyncio
        
        async def test():
            settings = Settings()
            service = SpeechService(settings)
            
            result = await service.synthesize(
                text="Hello, this is a test.",
                emotion="neutral",
                intensity=0.5
            )
            
            print(f"  ✓ Test synthesis successful!")
            print(f"    Output: {result.audio_path}")
            print(f"    Duration: {result.duration:.2f}s")
        
        asyncio.run(test())
        
    except Exception as e:
        print(f"Warning: Test synthesis failed: {e}")
        print("You may need to run the setup again or check dependencies.")


def main() -> None:
    """Main setup function."""
    print("=" * 60)
    print("Emotional Speech Generation - Setup")
    print("=" * 60)
    print()
    
    setup_directories()
    download_models()
    test_synthesis()
    
    print("\n" + "=" * 60)
    print("Setup complete!")
    print("=" * 60)
    print("\nYou can now run:")
    print("  • API: make run")
    print("  • CLI: python scripts/solution.py 'Hello world' output.wav")
    print()


if __name__ == "__main__":
    main()

