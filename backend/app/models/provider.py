"""Data models for model provider requests and responses."""
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class ProviderCompletionRequest(BaseModel):
    """Normalized prompt request sent to any ModelProvider implementation."""
    prompt: str = Field(description="User prompt / task input")
    system_prompt: str = Field(default="", description="System behavior instructions")
    json_mode: bool = Field(default=True, description="Enforce JSON output where supported")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=1024, ge=64, le=4096)


class ProviderStatus(BaseModel):
    """Health and availability report for a provider."""
    provider_name: str
    is_available: bool
    model_name: str
    latency_ms: Optional[float] = None
    message: Optional[str] = None
    extra_metadata: Dict[str, Any] = Field(default_factory=dict)
