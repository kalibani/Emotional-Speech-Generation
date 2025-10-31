"""Emotion metadata schemas."""

from typing import List
from pydantic import BaseModel, Field


class EmotionInfo(BaseModel):
    """Information about an emotion."""
    
    id: str = Field(..., description="Emotion identifier")
    name: str = Field(..., description="Display name")
    description: str = Field(..., description="Emotion description")
    recommended_intensity: float = Field(..., description="Recommended intensity value")
    use_cases: List[str] = Field(..., description="Typical use cases")


class EmotionsListResponse(BaseModel):
    """Response containing list of available emotions."""
    
    emotions: List[EmotionInfo] = Field(..., description="List of available emotions")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "emotions": [
                        {
                            "id": "neutral",
                            "name": "Neutral",
                            "description": "Standard documentary narration tone",
                            "recommended_intensity": 0.5,
                            "use_cases": ["facts", "introductions", "transitions"]
                        },
                        {
                            "id": "excited",
                            "name": "Excited",
                            "description": "Enthusiastic discovery or wonder",
                            "recommended_intensity": 0.7,
                            "use_cases": ["discoveries", "revelations"]
                        }
                    ]
                }
            ]
        }
    }

