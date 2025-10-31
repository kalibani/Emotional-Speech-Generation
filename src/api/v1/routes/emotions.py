"""Emotion metadata endpoints."""

from fastapi import APIRouter, Depends

from src.api.v1.schemas.emotions import EmotionsListResponse, EmotionInfo
from src.services.speech_service import SpeechService
from src.api.dependencies import get_speech_service

router = APIRouter(prefix="/emotions", tags=["emotions"])


@router.get("", response_model=EmotionsListResponse)
async def list_emotions(
    speech_service: SpeechService = Depends(get_speech_service)
) -> EmotionsListResponse:
    """
    Get list of available emotions.
    
    Returns information about all emotions supported by the TTS system,
    including their descriptions, recommended intensities, and use cases.
    
    **Returns:**
    - **emotions**: List of emotion objects with metadata
    """
    emotions_data = speech_service.list_emotions()
    
    emotions_list = [
        EmotionInfo(
            id=emotion_id,
            name=data["name"],
            description=data["description"],
            recommended_intensity=data["recommended_intensity"],
            use_cases=data["use_cases"]
        )
        for emotion_id, data in emotions_data.items()
    ]
    
    return EmotionsListResponse(emotions=emotions_list)


@router.get("/{emotion_id}", response_model=EmotionInfo)
async def get_emotion(
    emotion_id: str,
    speech_service: SpeechService = Depends(get_speech_service)
) -> EmotionInfo:
    """
    Get information about a specific emotion.
    
    **Parameters:**
    - **emotion_id**: Emotion identifier (e.g., "excited", "sad")
    
    **Returns:**
    Detailed information about the requested emotion.
    """
    from fastapi import HTTPException
    
    emotions_data = speech_service.list_emotions()
    
    if emotion_id not in emotions_data:
        available = ', '.join(emotions_data.keys())
        raise HTTPException(
            status_code=404,
            detail=f"Emotion '{emotion_id}' not found. Available: {available}"
        )
    
    data = emotions_data[emotion_id]
    return EmotionInfo(
        id=emotion_id,
        name=data["name"],
        description=data["description"],
        recommended_intensity=data["recommended_intensity"],
        use_cases=data["use_cases"]
    )

