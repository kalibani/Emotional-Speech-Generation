"""Text processing utilities for TTS."""

import re
from typing import List


class TextProcessor:
    """Process and normalize text for TTS synthesis."""

    def __init__(self, max_length: int = 5000):
        """Initialize text processor.
        
        Args:
            max_length: Maximum allowed text length
        """
        self.max_length = max_length

    def normalize(self, text: str) -> str:
        """Normalize text for TTS.
        
        Args:
            text: Input text
            
        Returns:
            Normalized text
            
        Raises:
            ValueError: If text is empty or too long
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())

        # Check length
        if len(text) > self.max_length:
            raise ValueError(
                f"Text too long: {len(text)} characters (max: {self.max_length})"
            )

        # Normalize punctuation
        text = self._normalize_punctuation(text)

        # Handle numbers
        text = self._expand_numbers(text)

        return text

    def _normalize_punctuation(self, text: str) -> str:
        """Normalize punctuation marks.
        
        Args:
            text: Input text
            
        Returns:
            Text with normalized punctuation
        """
        # Ensure punctuation has proper spacing
        text = re.sub(r'\s*([.,!?;:])\s*', r'\1 ', text)
        
        # Remove multiple punctuation
        text = re.sub(r'([.,!?;:]){2,}', r'\1', text)
        
        return text.strip()

    def _expand_numbers(self, text: str) -> str:
        """Expand numbers to words (basic implementation).
        
        Args:
            text: Input text
            
        Returns:
            Text with expanded numbers
        """
        # Simple number word mapping (extend as needed)
        number_words = {
            '0': 'zero', '1': 'one', '2': 'two', '3': 'three',
            '4': 'four', '5': 'five', '6': 'six', '7': 'seven',
            '8': 'eight', '9': 'nine', '10': 'ten'
        }
        
        # Replace standalone single-digit numbers
        for num, word in number_words.items():
            text = re.sub(rf'\b{num}\b', word, text)
        
        return text

    def chunk_text(self, text: str, max_chunk_size: int = 500) -> List[str]:
        """Split text into smaller chunks at sentence boundaries.
        
        Args:
            text: Input text
            max_chunk_size: Maximum characters per chunk
            
        Returns:
            List of text chunks
        """
        # Normalize first
        text = self.normalize(text)

        # Split into sentences
        sentences = re.split(r'([.!?])\s+', text)
        
        # Reconstruct sentences with punctuation
        reconstructed = []
        for i in range(0, len(sentences) - 1, 2):
            if i + 1 < len(sentences):
                reconstructed.append(sentences[i] + sentences[i + 1])
            else:
                reconstructed.append(sentences[i])

        # Group sentences into chunks
        chunks = []
        current_chunk = ""
        
        for sentence in reconstructed:
            if len(current_chunk) + len(sentence) <= max_chunk_size:
                current_chunk += " " + sentence if current_chunk else sentence
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    def detect_emotion_hints(self, text: str) -> str:
        """Detect emotion hints from text content (simple keyword-based).
        
        Args:
            text: Input text
            
        Returns:
            Suggested emotion
        """
        text_lower = text.lower()

        # Keyword-based emotion detection
        if any(word in text_lower for word in ['amazing', 'incredible', 'wow', 'exciting', 'discovery']):
            return 'excited'
        elif any(word in text_lower for word in ['sad', 'tragic', 'unfortunately', 'loss', 'died']):
            return 'sad'
        elif any(word in text_lower for word in ['warning', 'critical', 'important', 'attention']):
            return 'serious'
        elif any(word in text_lower for word in ['urgent', 'quickly', 'immediately', 'emergency']):
            return 'urgent'
        elif any(word in text_lower for word in ['heart', 'feel', 'empathy', 'understand']):
            return 'empathetic'
        else:
            return 'neutral'

