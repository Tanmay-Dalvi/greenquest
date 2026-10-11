"""Integration tests for FastAPI REST API endpoints."""
import pytest
import httpx
from backend.app.main import app


@pytest.mark.asyncio
async def test_health_endpoint():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "GreenQuest API"


@pytest.mark.asyncio
async def test_providers_endpoint():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/providers")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 3
        names = [p["provider_name"] for p in data]
        assert "fallback" in names
        assert "ollama" in names


@pytest.mark.asyncio
async def test_sample_mission_endpoint():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/missions/sample")
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "steps" in data
        assert len(data["steps"]) >= 2


@pytest.mark.asyncio
async def test_generate_mission_endpoint_valid_payload():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "duration_minutes": 25,
            "environment": "park",
            "mood": "curious",
            "energy_level": "moderate",
            "companion_type": "solo",
            "sensory_focus": ["sight", "sound"],
            "notes": "Near community pond",
        }
        response = await client.post("/api/missions/generate", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["environment"] == "park"
        assert data["estimated_duration_minutes"] == 25
        assert len(data["steps"]) >= 2
        assert "generator_info" in data


@pytest.mark.asyncio
async def test_generate_mission_endpoint_invalid_payload():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # Invalid duration (below 10 minutes)
        payload = {
            "duration_minutes": 2,
            "environment": "invalid_env",
        }
        response = await client.post("/api/missions/generate", json=payload)
        assert response.status_code == 422
