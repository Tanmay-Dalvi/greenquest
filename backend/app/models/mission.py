from enum import Enum
from typing import List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field, field_validator


class EnvironmentType(str, Enum):
    PARK = "park"
    FOREST = "forest"
    NEIGHBORHOOD = "neighborhood"
    GARDEN = "garden"
    WATERFRONT = "waterfront"
    TRAIL = "trail"


class MoodType(str, Enum):
    MINDFUL = "mindful"
    CURIOUS = "curious"
    PLAYFUL = "playful"
    CONTEMPLATIVE = "contemplative"
    ENERGIZED = "energized"


class EnergyLevel(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    BRISK = "brisk"


class CompanionType(str, Enum):
    SOLO = "solo"
    FAMILY = "family"
    FRIENDS = "friends"
    DOG = "dog"


class SensoryType(str, Enum):
    SIGHT = "sight"
    SOUND = "sound"
    TOUCH = "touch"
    SCENT = "scent"
    SPATIAL = "spatial"


class DifficultyLevel(str, Enum):
    EASY = "easy"
    MODERATE = "moderate"
    CHALLENGING = "challenging"


class MissionPreferenceRequest(BaseModel):
    """User input preferences for outdoor micro-adventure generation."""
    duration_minutes: int = Field(
        default=30,
        ge=10,
        le=120,
        description="Desired duration in minutes (10 to 120)"
    )
    environment: EnvironmentType = Field(
        default=EnvironmentType.PARK,
        description="Surrounding outdoor environment"
    )
    mood: MoodType = Field(
        default=MoodType.MINDFUL,
        description="Intended adventure atmosphere or mindset"
    )
    energy_level: EnergyLevel = Field(
        default=EnergyLevel.MODERATE,
        description="Physical exertion expectation"
    )
    companion_type: CompanionType = Field(
        default=CompanionType.SOLO,
        description="Who is participating in this quest"
    )
    sensory_focus: List[SensoryType] = Field(
        default_factory=lambda: [SensoryType.SIGHT, SensoryType.SOUND],
        description="Target sensory channels to engage"
    )
    notes: Optional[str] = Field(
        default=None,
        max_length=200,
        description="Optional local landmarks or context"
    )

    @field_validator("sensory_focus")
    @classmethod
    def validate_sensory_focus(cls, v: List[SensoryType]) -> List[SensoryType]:
        if not v:
            return [SensoryType.SIGHT, SensoryType.SOUND]
        return list(dict.fromkeys(v))  # Preserve order, deduplicate


class MissionStep(BaseModel):
    """An individual outdoor quest step or observation prompt."""
    step_number: int = Field(ge=1, description="1-based sequence index")
    title: str = Field(min_length=3, max_length=100, description="Concise task title")
    instruction: str = Field(min_length=10, max_length=500, description="Specific outdoor action")
    sensory_type: SensoryType = Field(description="Primary sensory modality")
    estimated_minutes: int = Field(ge=1, le=60, description="Estimated minutes for this task")
    completed: bool = Field(default=False, description="Completion toggle state")


class GeneratorInfo(BaseModel):
    """Metadata regarding how the mission was created."""
    provider: str = Field(description="Provider used, e.g. ollama, fallback, hosted")
    model: str = Field(description="Model identifier, e.g. gemma3:1b")
    fallback_used: bool = Field(default=False, description="True if deterministic fallback was triggered")
    generation_time_ms: int = Field(default=0, description="Time taken to orchestrate in milliseconds")
    safety_validated: bool = Field(default=True, description="Passed deterministic safety filters")


class MissionResponse(BaseModel):
    """Complete structured micro-adventure response delivered to client."""
    id: str = Field(description="Unique mission identifier")
    title: str = Field(min_length=5, max_length=120, description="Inspiring outdoor mission title")
    tagline: str = Field(min_length=10, max_length=200, description="Poetic sensory hook")
    environment: EnvironmentType
    estimated_duration_minutes: int = Field(ge=5, le=180)
    difficulty: DifficultyLevel = Field(default=DifficultyLevel.EASY)
    theme: str = Field(min_length=3, max_length=100)
    sensory_prompt: str = Field(min_length=10, max_length=300)
    leave_no_trace_principle: str = Field(min_length=10, max_length=300)
    safety_notes: List[str] = Field(min_length=1)
    steps: List[MissionStep] = Field(min_length=2, max_length=10)
    generator_info: GeneratorInfo
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SafetyReview(BaseModel):
    """Result of deterministic and LLM safety evaluation."""
    is_safe: bool = Field(description="True if mission passes all safety rules")
    violations: List[str] = Field(default_factory=list, description="Specific safety violations detected")
    recommendations: List[str] = Field(default_factory=list, description="Remediation guidance")
