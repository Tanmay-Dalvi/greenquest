"""Regression tests for Ollama Gemma 3 1B integration, output defects, and recovery."""
import json
import pytest
import httpx
from unittest.mock import patch, MagicMock
from backend.app.main import app
from backend.app.orchestrator.repair import clean_and_repair_json, MalformedModelOutputError
from backend.app.providers.ollama import OllamaProvider
from backend.app.models.provider import ProviderCompletionRequest
from backend.app.models.mission import MissionPreferenceRequest, EnvironmentType
from backend.app.orchestrator.machine import OrchestrationStateMachine


# Exact raw output defect observed from Gemma 3 1B on CPU
RAW_GEMMA_MALFORMED_OUTPUT = """{"title": "Quiet Canopy Walk", "tagline": "A mindful journey through the park's green spaces, focusing on sensory awareness and stillness.","theme": "Nature & Reflection", "sensory_prompt": "Observe the textures of leaves, the sound of wind through branches, and the dappled sunlight on the ground.","leave_no_trace_principle": "Leave only footprints, take only memories, and respect the natural world around you.","safety_notes": ["Stay on marked paths; avoid steep slopes or unstable areas.", "Be aware of wildlife; maintain a respectful distance.", "Watch for fallen branches or uneven terrain; proceed cautiously."], "steps": [
    {"step_number": 1, "title": "Rooted Observation", "instruction": "Slowly scan the ground with your eyes, noticing the subtle variations in texture and color of the soil.  Focus on the feeling of the earth beneath your feet, grounding yourself in the present moment.”}, {","sensory_type": "touch", "estimated_minutes": 10}, {"step_number": 2, "title": "Wind Whispers & Leaf Dance", "instruction": "Close your eyes and listen intently to the rustling leaves and the gentle breeze.  Notice how the wind shapes the patterns of the branches, creating a visual dance.  Allow your senses to become attuned to the natural flow.”}, {","sensory_type": "sight", "estimated_minutes": 15}, {"step_number": 3, "title": "Sunlit Stillness", "instruction": "Stand still for a moment, absorbing the warmth of the sun filtering through the canopy.  Notice the way the light plays across the landscape, creating a peaceful and serene ambiance.  Feel a quiet sense of calm and connection to the surroundings.”} ]} § § § § §"""


def test_regression_clean_and_repair_gemma3_defects():
    """Verify that clean_and_repair_json rescues the exact malformed Gemma 3 1B output."""
    data = clean_and_repair_json(RAW_GEMMA_MALFORMED_OUTPUT)
    assert data["title"] == "Quiet Canopy Walk"
    assert len(data["steps"]) == 3
    assert data["steps"][0]["sensory_type"] == "touch"
    assert data["steps"][1]["sensory_type"] == "sight"
    assert "present moment." in data["steps"][0]["instruction"]


def test_regression_clean_and_repair_truncated_json():
    """Verify repair when model output hits token limit mid-string."""
    truncated = '{"title": "Forest Peace", "theme": "Mindfulness", "steps": [{"step_number": 1, "title": "Gazing", "instruction": "Look at the canopy'
    data = clean_and_repair_json(truncated)
    assert data.get("title") == "Forest Peace"


def test_regression_clean_and_repair_empty_output_raises():
    """Verify MalformedModelOutputError on completely empty output."""
    with pytest.raises(MalformedModelOutputError):
        clean_and_repair_json("")


@pytest.mark.asyncio
async def test_regression_ollama_payload_includes_response_schema():
    """Verify OllamaProvider sets format to response_schema when provided."""
    provider = OllamaProvider(base_url="http://localhost:11434")
    schema = {"type": "object", "properties": {"theme": {"type": "string"}}}
    req = ProviderCompletionRequest(
        prompt="Test prompt",
        json_mode=True,
        response_schema=schema,
    )

    fake_response = MagicMock()
    fake_response.status_code = 200
    fake_response.json.return_value = {"response": '{"theme": "Woodland"}'}

    with patch("httpx.AsyncClient.post", return_value=fake_response) as mock_post:
        result = await provider.generate(req)
        assert mock_post.called
        call_kwargs = mock_post.call_args[1]
        assert call_kwargs["json"]["format"] == schema
        assert result == '{"theme": "Woodland"}'


from backend.app.providers.base import ProviderTimeoutError


@pytest.mark.asyncio
async def test_regression_successful_ollama_generation_mocked():
    """
    Test mocked Ollama mission generation via FastAPI endpoint.
    Verifies provider=ollama, fallback_used=False, and harmonized step durations.
    """
    responses = [
        json.dumps({
            "theme": "Sensory Canopy Exploration",
            "narrative_arc": "Step into the park, observe leaves, ground senses, and departures.",
            "target_step_count": 3,
            "difficulty": "easy",
            "allocated_minutes": 30,
        }),
        json.dumps({
            "title": "Canopy Exploration",
            "tagline": "Notice textures and breathe fresh morning air.",
            "theme": "Sensory Canopy Exploration",
            "sensory_prompt": "Awaken sight and hearing with stillness.",
            "leave_no_trace_principle": "Stay strictly on public paths and pack out waste.",
            "safety_notes": ["Stay aware of uneven footing on marked trails."],
            "steps": [
                {
                    "step_number": 1,
                    "title": "Look Up",
                    "instruction": "Scan the upper branches for gradations of green in sunlight.",
                    "sensory_type": "sight",
                    "estimated_minutes": 5,
                },
                {
                    "step_number": 2,
                    "title": "Listen to Wind",
                    "instruction": "Close eyes and count distinct ambient nature sounds.",
                    "sensory_type": "sound",
                    "estimated_minutes": 10,
                },
                {
                    "step_number": 3,
                    "title": "Bark Touch",
                    "instruction": "Press fingertips against fallen dry bark on the path verge.",
                    "sensory_type": "touch",
                    "estimated_minutes": 15,
                },
            ],
        }),
    ]

    async def mock_generate(req):
        if responses:
            return responses.pop(0)
        return responses[-1]

    with patch.object(OllamaProvider, "generate", side_effect=mock_generate):
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            payload = {
                "duration_minutes": 30,
                "environment": "park",
                "mood": "mindful",
                "energy_level": "moderate",
                "companion_type": "solo",
                "sensory_focus": ["sight", "sound"],
            }
            res = await client.post("/api/missions/generate", json=payload)
            assert res.status_code == 200
            data = res.json()
            assert data["generator_info"]["provider"] == "ollama"
            assert data["generator_info"]["fallback_used"] is False
            assert data["generator_info"]["model"] == "gemma3:1b"
            assert len(data["steps"]) == 3
            total_step_mins = sum(s["estimated_minutes"] for s in data["steps"])
            assert total_step_mins == 30


@pytest.mark.asyncio
async def test_regression_ollama_timeout_triggers_safe_fallback():
    """Verify that an Ollama ReadTimeout/ProviderTimeout gracefully activates deterministic fallback."""
    with patch.object(OllamaProvider, "generate", side_effect=ProviderTimeoutError("Ollama timed out")):
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            payload = {
                "duration_minutes": 25,
                "environment": "garden",
                "mood": "curious",
            }
            res = await client.post("/api/missions/generate", json=payload)
            assert res.status_code == 200
            data = res.json()
            assert data["generator_info"]["provider"] == "fallback"
            assert data["generator_info"]["fallback_used"] is True
            assert data["environment"] == "garden"
            assert len(data["steps"]) >= 2

