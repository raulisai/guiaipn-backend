"""
Tests de integración de la API
"""
import pytest


def test_health_endpoint(client):
    """Test del endpoint de health check"""
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"
    assert data["service"] == "guiaipn-backend"


def test_auth_verify_without_token(client):
    """Test de verificación sin token"""
    response = client.post("/api/v1/auth/verify", json={})
    
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
