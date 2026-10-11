"""Abstract Base Class for Model Providers in GreenQuest."""
from abc import ABC, abstractmethod
from backend.app.models.provider import ProviderCompletionRequest, ProviderStatus


class ProviderError(Exception):
    """Base exception for provider failures."""
    pass


class ProviderUnavailableError(ProviderError):
    """Raised when the provider runtime/server cannot be reached."""
    pass


class ProviderTimeoutError(ProviderError):
    """Raised when provider inference exceeds allotted timeout."""
    pass


class ModelProvider(ABC):
    """Interface defining requirements for an LLM provider."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Identifying name of the provider."""
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Active model identifier."""
        pass

    @abstractmethod
    async def generate(self, request: ProviderCompletionRequest) -> str:
        """
        Generate raw text response from the model.
        Raises ProviderUnavailableError or ProviderTimeoutError on failure.
        """
        pass

    @abstractmethod
    async def check_availability(self) -> ProviderStatus:
        """
        Check health and responsiveness of the model backend.
        Must not raise exceptions; returns ProviderStatus with is_available boolean.
        """
        pass

