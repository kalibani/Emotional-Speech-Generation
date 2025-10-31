"""Audio post-processing utilities."""

import numpy as np
import soundfile as sf
from scipy import signal
from pathlib import Path
from typing import Tuple


class AudioProcessor:
    """Process and enhance synthesized audio."""

    def __init__(self, sample_rate: int = 24000):
        """Initialize audio processor.
        
        Args:
            sample_rate: Target sample rate in Hz
        """
        self.sample_rate = sample_rate

    def normalize_audio(self, audio: np.ndarray, target_level: float = -20.0) -> np.ndarray:
        """Normalize audio to target loudness level.
        
        Args:
            audio: Input audio array
            target_level: Target loudness in dB
            
        Returns:
            Normalized audio array
        """
        # Calculate RMS
        rms = np.sqrt(np.mean(audio ** 2))
        
        if rms > 0:
            # Convert to dB
            current_level = 20 * np.log10(rms)
            
            # Calculate gain
            gain_db = target_level - current_level
            gain = 10 ** (gain_db / 20)
            
            # Apply gain
            audio = audio * gain
            
            # Prevent clipping
            audio = np.clip(audio, -1.0, 1.0)
        
        return audio

    def remove_silence(
        self, 
        audio: np.ndarray, 
        threshold: float = -40.0,
        min_silence_duration: float = 0.3
    ) -> np.ndarray:
        """Remove long silence from audio.
        
        Args:
            audio: Input audio array
            threshold: Silence threshold in dB
            min_silence_duration: Minimum silence duration to remove (seconds)
            
        Returns:
            Audio with silence removed
        """
        # Calculate frame energy
        frame_length = int(0.02 * self.sample_rate)  # 20ms frames
        hop_length = frame_length // 2
        
        # Calculate energy per frame
        energy = np.array([
            np.sum(audio[i:i + frame_length] ** 2)
            for i in range(0, len(audio) - frame_length, hop_length)
        ])
        
        # Convert to dB
        energy_db = 10 * np.log10(energy + 1e-10)
        
        # Identify non-silent frames
        non_silent = energy_db > threshold
        
        # Expand frame decisions to samples
        mask = np.repeat(non_silent, hop_length)
        mask = mask[:len(audio)]
        
        # Ensure mask covers all samples
        if len(mask) < len(audio):
            mask = np.pad(mask, (0, len(audio) - len(mask)), constant_values=True)
        
        return audio[mask]

    def apply_compression(
        self, 
        audio: np.ndarray, 
        threshold: float = -20.0,
        ratio: float = 4.0
    ) -> np.ndarray:
        """Apply dynamic range compression.
        
        Args:
            audio: Input audio array
            threshold: Compression threshold in dB
            ratio: Compression ratio
            
        Returns:
            Compressed audio
        """
        # Simple compression implementation
        threshold_linear = 10 ** (threshold / 20)
        
        # Calculate envelope
        envelope = np.abs(audio)
        
        # Apply compression
        mask = envelope > threshold_linear
        audio[mask] = audio[mask] / (1 + (envelope[mask] - threshold_linear) * (ratio - 1) / ratio)
        
        return audio

    def resample(self, audio: np.ndarray, orig_sr: int, target_sr: int) -> np.ndarray:
        """Resample audio to target sample rate.
        
        Args:
            audio: Input audio array
            orig_sr: Original sample rate
            target_sr: Target sample rate
            
        Returns:
            Resampled audio
        """
        if orig_sr == target_sr:
            return audio
        
        # Calculate resampling ratio
        num_samples = int(len(audio) * target_sr / orig_sr)
        
        # Use scipy's resample
        return signal.resample(audio, num_samples)

    def change_speed(self, audio: np.ndarray, speed: float) -> np.ndarray:
        """Change audio playback speed.
        
        Args:
            audio: Input audio array
            speed: Speed multiplier (0.5-2.0, where 1.0 is original speed)
            
        Returns:
            Speed-adjusted audio
        """
        if speed == 1.0:
            return audio
        
        # Calculate new length
        new_length = int(len(audio) / speed)
        
        # Resample to change speed
        return signal.resample(audio, new_length)

    def save_audio(
        self, 
        audio: np.ndarray, 
        output_path: str | Path,
        sample_rate: int | None = None
    ) -> None:
        """Save audio to file.
        
        Args:
            audio: Audio array to save
            output_path: Output file path
            sample_rate: Sample rate (uses instance default if not provided)
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        sr = sample_rate or self.sample_rate
        
        # Ensure audio is in correct format
        audio = np.clip(audio, -1.0, 1.0)
        
        sf.write(str(output_path), audio, sr, subtype='PCM_16')

    def load_audio(self, audio_path: str | Path) -> Tuple[np.ndarray, int]:
        """Load audio from file.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Tuple of (audio array, sample rate)
        """
        audio, sample_rate = sf.read(str(audio_path))
        return audio, sample_rate

    def process_pipeline(
        self,
        audio: np.ndarray,
        normalize: bool = True,
        remove_silence: bool = False,
        compress: bool = False,
        speed: float = 1.0
    ) -> np.ndarray:
        """Apply complete audio processing pipeline.
        
        Args:
            audio: Input audio array
            normalize: Whether to normalize audio
            remove_silence: Whether to remove silence
            compress: Whether to apply compression
            speed: Speed adjustment factor
            
        Returns:
            Processed audio
        """
        # Apply speed change
        if speed != 1.0:
            audio = self.change_speed(audio, speed)
        
        # Remove silence
        if remove_silence:
            audio = self.remove_silence(audio)
        
        # Apply compression
        if compress:
            audio = self.apply_compression(audio)
        
        # Normalize
        if normalize:
            audio = self.normalize_audio(audio)
        
        return audio

