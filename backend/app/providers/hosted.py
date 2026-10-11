"""Optional Hosted Open-Weight Model Provider adapter (OpenAI-compatible)."""
import time
import httpx
from typing import Optional
from backend.app.config import settings
from backend.app.models.provider import ProviderCompletionRequest, ProviderStatus
from backend.app.providers.base import (
    ModelProvider,
    ProviderUnavailableError,
    ProviderTimeoutError,
    ProviderError,
)


class HostedProvider(ModelProvider):
    """Optional adapter for hosted open-weight endpoints (e.g. Together, Groq, Ollama remote)."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
    ):
        self._base_url = (base_url or settings.HOSTED_API_BASE_URL).rstrip("/")
        self._api_key = api_key or settings.HOSTED_API_KEY
        self._model_name = model_name or settings.HOSTED_MODEL

    @property
    def name(self) -> str:
        return "hosted"

    @property
    def model_name(self) -> str:
        return self._model_name

    async def generate(self, request: ProviderCompletionRequest) -> str:
        if not self._api_key:
            raise ProviderUnavailableError("HOSTED_API_KEY is not configured.")

        endpoint = f"{self._base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        messages = []
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})
        messages.append({"role": "user", "content": request.prompt})

        payload = {
            "model": self._model_name,
            "messages": messages,
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
        }
        if request.json_mode:
            payload["response_format"] = {"type": "json_object"}

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(endpoint, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                choices = data.get("choices", [])
                if not choices:
                    raise ProviderError("Hosted API returned no choices.")
                return choices[0]["message"]["content"]
        except httpx.ConnectError as exc:
            raise ProviderUnavailableError(f"Cannot reach hosted provider at {self._base_url}") from exc
        except httpx.TimeoutException as exc:
            raise ProviderTimeoutError(f"Hosted provider timed out for model {self._model_name}") from exc
        except Exception as exc:
            raise ProviderError(f"Hosted provider error: {str(exc)}") from exc

    async def check_availability() -> ProviderStatus:
        pass

    async def check_availability(self) -> ProviderStatus:
        if not self._api_key:
            return ProviderStatus(
                provider_name=self.name,
                is_available=False,
                model_name=self._model_name,
                message="Hosted provider not configured (HOSTED_API_KEY missing)",
            )
        return ProviderStatus(
            provider_name=self.name,
            is_available=True,
            model_name=self._model_name,
            message="Hosted provider configured",
        )
