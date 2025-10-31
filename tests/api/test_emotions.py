"""API emotion endpoints tests."""

import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


class TestEmotionEndpoints:
    """Test suite for emotion endpoints."""
    
    def test_list_emotions(self):
        """Test listing all emotions."""
        response = client.get("/v1/emotions")
        assert response.status_code == 200
        
        data = response.json()
        assert "emotions" in data
        assert len(data["emotions"]) > 0
        
        # Check first emotion structure
        emotion = data["emotions"][0]
        assert "id" in emotion
        assert "name" in emotion
        assert "description" in emotion
        assert "recommended_intensity" in emotion
        assert "use_cases" in emotion
    
    def test_get_specific_emotion(self):
        """Test getting a specific emotion."""
        response = client.get("/v1/emotions/excited")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == "excited"
        assert data["name"] == "Excited"
    
    def test_get_invalid_emotion(self):
        """Test getting an invalid emotion returns 404."""
        response = client.get("/v1/emotions/invalid_emotion")
        assert response.status_code == 404

