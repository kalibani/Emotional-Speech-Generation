#!/usr/bin/env python3
"""
CLI for Emotional Speech Generation

This script provides a command-line interface for generating emotional speech.

Usage:
    python solution.py "Hello world" output.wav
    python solution.py "This is amazing!" output.wav --emotion excited --intensity 0.8
    python solution.py --help
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.speech_service import SpeechService
from config.settings import Settings
import asyncio


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Generate emotional speech from text",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  python solution.py "Hello world" output.wav
  
  # With emotion and intensity
  python solution.py "This is amazing!" output.wav --emotion excited --intensity 0.8
  
  # Different emotions
  python solution.py "Sadly, this happened." output.wav --emotion sad --intensity 0.6
  python solution.py "This is serious." output.wav --emotion serious

Available emotions: neutral, excited, sad, serious, empathetic, urgent
        """
    )
    
    parser.add_argument(
        "text",
        type=str,
        help="Text to synthesize (or --input for file)"
    )
    
    parser.add_argument(
        "output",
        type=str,
        help="Output audio file path (.wav, .mp3, .ogg)"
    )
    
    parser.add_argument(
        "--emotion",
        type=str,
        default="neutral",
        choices=["neutral", "excited", "sad", "serious", "empathetic", "urgent"],
        help="Emotion to apply (default: neutral)"
    )
    
    parser.add_argument(
        "--intensity",
        type=float,
        default=0.5,
        help="Emotion intensity from 0.0 to 1.0 (default: 0.5)"
    )
    
    parser.add_argument(
        "--input",
        type=str,
        help="Read text from file instead of command line"
    )
    
    parser.add_argument(
        "--sample-rate",
        type=int,
        default=24000,
        choices=[16000, 22050, 24000, 44100],
        help="Sample rate in Hz (default: 24000)"
    )
    
    parser.add_argument(
        "--no-normalize",
        action="store_true",
        help="Disable audio normalization"
    )
    
    parser.add_argument(
        "--remove-silence",
        action="store_true",
        help="Remove long silences from audio"
    )
    
    parser.add_argument(
        "--speed",
        type=float,
        default=1.0,
        help="Playback speed multiplier (0.5-2.0, default: 1.0)"
    )
    
    parser.add_argument(
        "--list-emotions",
        action="store_true",
        help="List available emotions and exit"
    )
    
    return parser.parse_args()


async def synthesize_speech(args: argparse.Namespace) -> None:
    """Synthesize speech based on command-line arguments.
    
    Args:
        args: Parsed command-line arguments
    """
    # Get text from file or command line
    if args.input:
        try:
            with open(args.input, 'r', encoding='utf-8') as f:
                text = f.read().strip()
        except FileNotFoundError:
            print(f"Error: Input file '{args.input}' not found", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error reading input file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        text = args.text
    
    # Validate inputs
    if not text:
        print("Error: Text cannot be empty", file=sys.stderr)
        sys.exit(1)
    
    if not 0.0 <= args.intensity <= 1.0:
        print("Error: Intensity must be between 0.0 and 1.0", file=sys.stderr)
        sys.exit(1)
    
    if not 0.5 <= args.speed <= 2.0:
        print("Error: Speed must be between 0.5 and 2.0", file=sys.stderr)
        sys.exit(1)
    
    # Validate output path
    output_path = Path(args.output)
    output_format = output_path.suffix.lstrip('.')
    if output_format not in ['wav', 'mp3', 'ogg']:
        print(f"Error: Unsupported output format '{output_format}'. Use .wav, .mp3, or .ogg", file=sys.stderr)
        sys.exit(1)
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Initialize settings and service
    print(f"Initializing TTS system (emotion: {args.emotion}, intensity: {args.intensity})...")
    
    try:
        settings = Settings()
        speech_service = SpeechService(settings)
        
        # Synthesize
        print(f"Synthesizing: \"{text[:50]}{'...' if len(text) > 50 else ''}\"")
        
        options = {
            "normalize_audio": not args.no_normalize,
            "remove_silence": args.remove_silence,
            "speed": args.speed
        }
        
        result = await speech_service.synthesize(
            text=text,
            emotion=args.emotion,
            intensity=args.intensity,
            output_format=output_format,
            sample_rate=args.sample_rate,
            options=options
        )
        
        # Copy result to desired output path
        import shutil
        shutil.copy(result.audio_path, args.output)
        
        # Print success message
        print(f"\n✓ Speech generated successfully!")
        print(f"  Output: {args.output}")
        print(f"  Duration: {result.duration:.2f} seconds")
        print(f"  Emotion: {args.emotion} (intensity: {args.intensity})")
        print(f"  Model: {result.model_name}")
        
    except ValueError as e:
        print(f"Validation error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error during synthesis: {e}", file=sys.stderr)
        sys.exit(1)


def list_emotions() -> None:
    """List available emotions and their descriptions."""
    from src.core.emotion_controller import EmotionController
    
    controller = EmotionController()
    emotions = controller.list_emotions()
    
    print("\nAvailable Emotions:\n")
    print(f"{'ID':<12} {'Name':<15} {'Intensity':<12} Description")
    print("-" * 80)
    
    for emotion_id, config in emotions.items():
        print(f"{emotion_id:<12} {config.name:<15} {config.recommended_intensity:<12.1f} {config.description}")
        print(f"{'':>27} Use cases: {', '.join(config.use_cases)}")
        print()


def main() -> None:
    """Main entry point."""
    args = parse_arguments()
    
    # Handle list emotions
    if args.list_emotions:
        list_emotions()
        sys.exit(0)
    
    # Run synthesis
    try:
        asyncio.run(synthesize_speech(args))
    except KeyboardInterrupt:
        print("\nInterrupted by user", file=sys.stderr)
        sys.exit(130)


if __name__ == "__main__":
    main()

