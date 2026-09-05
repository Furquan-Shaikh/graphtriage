"""
Day 1 smoke test for inference-service.
Run with: pytest tests/test_health.py
"""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint_returns_up():
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["service"] == "inference-service"
    assert body["status"] == "UP"
