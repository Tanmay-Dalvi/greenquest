"""Unit tests for Pydantic schema validation and defaults."""
import pytest
from pydantic import ValidationError
from backend.app.models.mission import (
    EnvironmentType,
    MoodType,
    EnergyLevel,
    SensoryType,
    DifficultyLevel,
    MissionPreferenceRequest,
    MissionStep,
    MissionResponse,
    GeneratorInfo,
)


def test_preference_request_defaults():
    req = MissionPreferenceRequest()
    assert req.duration_minutes == 30
    assert req.environment == EnvironmentType.PARK
    assert req.mood == MoodType.MINDFUL
    assert req.energy_level == EnergyLevel.MODERATE
    assert SensoryType.SIGHT in req.sensory_focus
    assert SensoryType.SOUND in req.sensory_focus


def test_preference_request_bounds():
    # Valid duration boundaries
    req_min = MissionPreferenceRequest(duration_minutes=10)
    assert req_min.duration_minutes == 10
    req_max = MissionPreferenceRequest(duration_minutes=120)
    assert req_max.duration_minutes == 120

    # Invalid low duration
    with pytest.raises(ValidationError):
        MissionPreferenceRequest(duration_minutes=5)

    # Invalid high duration
    with pytest.raises(ValidationError):
        MissionPreferenceRequest(duration_minutes=150)


def test_sensory_focus_deduplication_and_fallback():
    # Duplicates should be stripped
    req = MissionPreferenceRequest(sensory_focus=[SensoryType.SIGHT, SensoryType.SIGHT, SensoryType.TOUCH])
    assert len(req.sensory_focus) == 2
    assert req.sensory_focus == [SensoryType.SIGHT, SensoryType.TOUCH]

    # Empty list should default back to sight + sound
    req_empty = MissionPreferenceRequest(sensory_focus=[])
    assert len(req_empty.sensory_focus) == 2


def test_mission_step_validation():
    step = MissionStep(
        step_number=1,
        title="Canopy Breath",
        instruction="Pause and notice five distinct leaf shapes above.",
        sensory_type=SensoryType.SIGHT,
        estimated_minutes=5,
    )
    assert step.step_number == 1
    assert step.completed is False

    # Short instruction fails validation
    with pytest.raises(ValidationError):
        MissionStep(
            step_number=1,
            title="Step",
            instruction="Look.",  # Too short (<10 chars)
            sensory_type=SensoryType.SIGHT,
            estimated_minutes=5,
        )


def test_mission_response_serialization():
    step1 = MissionStep(
        step_number=1,
        title="Initial Observation",
        instruction="Look around for two distinct shades of green foliage.",
        sensory_type=SensoryType.SIGHT,
        estimated_minutes=5,
    )
    step2 = MissionStep(
        step_number=2,
        title="Canopy Listening",
        instruction="Close your eyes for 3 minutes and count distinct bird calls.",
        sensory_type=SensoryType.SOUND,
        estimated_minutes=5,
    )
    response = MissionResponse(
        id="gq-test-123",
        title="Sensory Haven Exploration",
        tagline="Ground your senses in the forest canopy.",
        environment=EnvironmentType.FOREST,
        estimated_duration_minutes=20,
        difficulty=DifficultyLevel.EASY,
        theme="Mindful Woodland",
        sensory_prompt="Tune your hearing to birdcalls before opening your eyes.",
        leave_no_trace_principle="Pack out all trash and stick to marked footpaths.",
        safety_notes=["Stay on marked trails.", "Watch for uneven tree roots."],
        steps=[step1, step2],
        generator_info=GeneratorInfo(
            provider="test",
            model="unit-test",
            fallback_used=False,
            generation_time_ms=10,
            safety_validated=True,
        ),
    )
    data = response.model_dump()
    assert data["id"] == "gq-test-123"
    assert len(data["steps"]) == 2
    assert data["generator_info"]["provider"] == "test"
