"""API health endpoint tests."""

import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


class TestHealthEndpoints:
    """Test suite for health check endpoints."""
    
    def test_health_check(self):
        """Test basic health check endpoint."""
        response = client.get("/v1/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "model_loaded" in data
        assert "timestamp" in data
    
    def test_readiness_check(self):
        """Test readiness check endpoint."""
        response = client.get("/v1/health/ready")
        # May be 200 or 503 depending on model loading
        assert response.status_code in [200, 503]
    
    def test_root_endpoint(self):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "docs" in data

