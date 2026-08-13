import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestAPI:
    def test_health_endpoint(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_list_restaurants(self):
        response = client.get("/restaurants")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_restaurant_by_id(self):
        response = client.get("/restaurants/R001")
        if response.status_code == 200:
            data = response.json()
            assert data["restaurant_id"] == "R001"
            assert "name" in data

    def test_chat_endpoint(self):
        response = client.post("/chat", json={
            "session_id": "test-session",
            "message": "Suggest a Korean restaurant in Thamel",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == "test-session"
        assert "intent" in data
        assert "response" in data
