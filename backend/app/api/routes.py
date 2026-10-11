from datetime import datetime, timezone
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, Depends
from backend.app.config import settings
from backend.app.models.mission import (
    MissionPreferenceRequest,
    MissionResponse,
)
from backend.app.models.provider import ProviderStatus
from backend.app.providers.base import ModelProvider
from backend.app.providers.ollama import OllamaProvider
from backend.app.providers.hosted import HostedProvider
from backend.app.providers.fallback import DeterministicFallbackProvider
from backend.app.orchestrator.machine import OrchestrationStateMachine

router = APIRouter(prefix="/api", tags=["missions"])

# Cached provider instances
_ollama_provider = OllamaProvider()
_hosted_provider = HostedProvider()
_fallback_provider = DeterministicFallbackProvider()


def get_active_provider() -> ModelProvider:
    """Resolve configured model provider."""
    if settings.FORCE_FALLBACK or settings.MODEL_PROVIDER == "fallback":
        return _fallback_provider
    elif settings.MODEL_PROVIDER == "hosted":
        return _hosted_provider
    return _ollama_provider


@router.post("/missions/generate", response_model=MissionResponse)
async def generate_mission(
    preferences: MissionPreferenceRequest,
    provider: ModelProvider = Depends(get_active_provider),
) -> MissionResponse:
    """
    Generate an outdoor micro-adventure based on user preferences.
    Executes multi-agent orchestrator with deterministic safety filters and fallback.
    """
    try:
        orchestrator = OrchestrationStateMachine(
            provider=provider,
            fallback_provider=_fallback_provider,
            max_retries=settings.MAX_SAFETY_RETRIES,
        )
        mission = await orchestrator.execute(preferences)
        return mission
    except Exception as exc:
        # Fallback safeguard in case anything escapes
        return _fallback_provider.generate_mission_sync(preferences)


@router.get("/missions/sample", response_model=MissionResponse)
async def get_sample_mission() -> MissionResponse:
    """Returns a baseline validated sample mission for instant preview."""
    return _fallback_provider.generate_mission_sync(MissionPreferenceRequest())


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Service health and uptime report."""
    return {
        "status": "healthy",
        "service": "GreenQuest API",
        "version": "0.1.0",
        "configured_provider": settings.MODEL_PROVIDER,
        "force_fallback": settings.FORCE_FALLBACK,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/providers", response_model=List[ProviderStatus])
async def list_providers_status() -> List[ProviderStatus]:
    """Check and report health status of all supported inference providers."""
    ollama_status = await _ollama_provider.check_availability()
    hosted_status = await _hosted_provider.check_availability()
    fallback_status = await _fallback_provider.check_availability()

    return [ollama_status, hosted_status, fallback_status]
