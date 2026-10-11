"""Unit tests for model providers and deterministic fallback."""
import pytest
from backend.app.models.mission import (
    EnvironmentType,
    MoodType,
    MissionPreferenceRequest,
)
from backend.app.models.provider import ProviderCompletionRequest
from backend.app.providers.fallback import DeterministicFallbackProvider
from backend.app.providers.ollama import OllamaProvider
from backend.app.providers.hosted import HostedProvider
from backend.app.providers.base import ProviderUnavailableError


@pytest.mark.asyncio
async def test_fallback_provider_availability():
    provider = DeterministicFallbackProvider()
    status = await provider.check_availability()
    assert status.is_available is True
    assert status.provider_name == "fallback"


def test_fallback_provider_generates_valid_mission_across_environments():
    provider = DeterministicFallbackProvider()

    for env in EnvironmentType:
        req = MissionPreferenceRequest(
            environment=env,
            duration_minutes=45,
            mood=MoodType.CURIOUS,
        )
        mission = provider.generate_mission_sync(req)

        assert mission.id.startswith(f"gq-{env.value}-")
        assert mission.environment == env
        assert mission.estimated_duration_minutes == 45
        assert len(mission.steps) >= 3
        assert mission.generator_info.fallback_used is True
        assert mission.generator_info.provider == "fallback"
        assert len(mission.leave_no_trace_principle) > 10
        assert len(mission.safety_notes) >= 1

        # Check total estimated minutes matches roughly
        total_step_mins = sum(s.estimated_minutes for s in mission.steps)
        assert total_step_mins == 45


@pytest.mark.asyncio
async def test_fallback_provider_completion_interface():
    provider = DeterministicFallbackProvider()
    req = ProviderCompletionRequest(prompt="test prompt")
    raw = await provider.generate(req)
    assert "gq-" in raw
    assert "title" in raw


@pytest.mark.asyncio
async def test_ollama_provider_unreachable_behavior():
    # Use invalid port to verify graceful failure
    provider = OllamaProvider(base_url="http://127.0.0.1:54321", timeout_seconds=1.0)
    status = await provider.check_availability()
    assert status.is_available is False
    assert "unreachable" in status.message.lower() or "cannot connect" in status.message.lower()

    with pytest.raises(ProviderUnavailableError):
        await provider.generate(ProviderCompletionRequest(prompt="hello"))


@pytest.mark.asyncio
async def test_hosted_provider_unconfigured():
    provider = HostedProvider(api_key="")
    status = await provider.check_availability()
    assert status.is_available is False
    assert "missing" in status.message.lower() or "not configured" in status.message.lower()

    with pytest.raises(ProviderUnavailableError):
        await provider.generate(ProviderCompletionRequest(prompt="hello"))
