"""Unit tests for Orchestrator State Machine, agents, bounded retries, and fallback."""
import json
import pytest
from backend.app.models.mission import (
    EnvironmentType,
    MoodType,
    MissionPreferenceRequest,
)
from backend.app.models.provider import ProviderCompletionRequest, ProviderStatus
from backend.app.providers.base import ModelProvider, ProviderUnavailableError
from backend.app.providers.fallback import DeterministicFallbackProvider
from backend.app.orchestrator.machine import OrchestrationStateMachine


class MockFailingProvider(ModelProvider):
    @property
    def name(self) -> str:
        return "mock_failing"

    @property
    def model_name(self) -> str:
        return "mock_failing_model"

    async def generate(self, request: ProviderCompletionRequest) -> str:
        raise ProviderUnavailableError("Model server connection lost")

    async def check_availability(self) -> ProviderStatus:
        return ProviderStatus(
            provider_name=self.name,
            is_available=False,
            model_name=self.model_name,
            message="Server down",
        )


class MockUnsafeThenSafeProvider(ModelProvider):
    """Returns an unsafe plan on attempt 1, then safe plan on attempt 2."""
    def __init__(self):
        self.call_count = 0

    @property
    def name(self) -> str:
        return "mock_remediation"

    @property
    def model_name(self) -> str:
        return "mock_remediation_model"

    async def generate(self, request: ProviderCompletionRequest) -> str:
        self.call_count += 1
        # If this is the planner call
        if "GreenQuest Outdoor Adventure Planner" in request.system_prompt:
            return json.dumps({
                "theme": "Remediated Forest Path",
                "narrative_arc": "Listen and observe.",
                "target_step_count": 2,
                "difficulty": "easy",
                "allocated_minutes": 20,
            })

        # Activity Agent calls
        if self.call_count <= 2:
            # Unsafe on first generation (encourages berry tasting)
            return json.dumps({
                "title": "Unsafe Quest",
                "tagline": "Taste the wild things.",
                "theme": "Wild Foraging",
                "sensory_prompt": "Taste wild berries.",
                "leave_no_trace_principle": "Respect nature.",
                "safety_notes": ["Be careful."],
                "steps": [
                    {"step_number": 1, "title": "Forage", "instruction": "Eat some wild berries along the path.", "sensory_type": "sight", "estimated_minutes": 5},
                    {"step_number": 2, "title": "Listen", "instruction": "Listen to the birds.", "sensory_type": "sound", "estimated_minutes": 5},
                ],
            })
        else:
            # Safe on second generation after remediation note
            return json.dumps({
                "title": "Safe Sensory Walk",
                "tagline": "Notice five shades of green.",
                "theme": "Safe Woodland",
                "sensory_prompt": "Listen and look.",
                "leave_no_trace_principle": "Stay on marked trails and pack out waste.",
                "safety_notes": ["Stay alert on gravel."],
                "steps": [
                    {"step_number": 1, "title": "Gazing", "instruction": "Observe leaf patterns high in the tree canopy.", "sensory_type": "sight", "estimated_minutes": 5},
                    {"step_number": 2, "title": "Listening", "instruction": "Close your eyes and count three bird calls.", "sensory_type": "sound", "estimated_minutes": 5},
                ],
            })

    async def check_availability(self) -> ProviderStatus:
        return ProviderStatus(provider_name=self.name, is_available=True, model_name=self.model_name)


@pytest.mark.asyncio
async def test_orchestrator_with_fallback_provider():
    provider = DeterministicFallbackProvider()
    machine = OrchestrationStateMachine(provider=provider)

    req = MissionPreferenceRequest(
        environment=EnvironmentType.GARDEN,
        duration_minutes=30,
        mood=MoodType.MINDFUL,
    )
    mission = await machine.execute(req)

    assert mission.environment == EnvironmentType.GARDEN
    assert mission.estimated_duration_minutes == 30
    assert len(mission.steps) >= 2
    assert mission.generator_info.fallback_used is True


@pytest.mark.asyncio
async def test_orchestrator_automatic_fallback_on_provider_error():
    failing_provider = MockFailingProvider()
    machine = OrchestrationStateMachine(provider=failing_provider)

    req = MissionPreferenceRequest(
        environment=EnvironmentType.PARK,
        duration_minutes=25,
    )
    mission = await machine.execute(req)

    # Must return valid mission via fallback rather than throwing uncaught error
    assert mission is not None
    assert mission.generator_info.fallback_used is True
    assert mission.environment == EnvironmentType.PARK
    assert len(mission.steps) >= 2


@pytest.mark.asyncio
async def test_orchestrator_bounded_retry_and_remediation():
    mock_provider = MockUnsafeThenSafeProvider()
    machine = OrchestrationStateMachine(provider=mock_provider, max_retries=2)

    req = MissionPreferenceRequest(
        environment=EnvironmentType.FOREST,
        duration_minutes=20,
    )
    mission = await machine.execute(req)

    # Successfully repaired after retry!
    assert mission.title == "Safe Sensory Walk"
    assert mission.generator_info.fallback_used is False
    assert mission.generator_info.safety_validated is True
    assert len(mission.steps) == 2
