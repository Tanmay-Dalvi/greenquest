"""Ollama Local Model Provider implementation targeting Gemma 3 1B."""
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


class OllamaProvider(ModelProvider):
    """Integrates with locally running Ollama daemon."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        model_name: Optional[str] = None,
        timeout_seconds: Optional[float] = None,
    ):
        self._base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        self._model_name = model_name or settings.OLLAMA_MODEL
        self._timeout_seconds = timeout_seconds or settings.OLLAMA_TIMEOUT_SECONDS

    @property
    def name(self) -> str:
        return "ollama"

    @property
    def model_name(self) -> str:
        return self._model_name

    async def generate(self, request: ProviderCompletionRequest) -> str:
        """Call Ollama /api/generate endpoint."""
        endpoint = f"{self._base_url}/api/generate"
        payload = {
            "model": self._model_name,
            "prompt": request.prompt,
            "system": request.system_prompt,
            "stream": False,
            "options": {
                "temperature": request.temperature,
                "num_predict": request.max_tokens,
            },
        }
        if request.response_schema:
            payload["format"] = request.response_schema
        elif request.json_mode:
            payload["format"] = "json"

        start_time = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=self._timeout_seconds) as client:
                response = await client.post(endpoint, json=payload)
                response.raise_for_status()
                data = response.json()
                raw_text = data.get("response", "")
                if not raw_text:
                    raise ProviderError("Empty response returned by Ollama")
                return raw_text

        except httpx.ConnectError as exc:
            raise ProviderUnavailableError(
                f"Cannot connect to Ollama at {self._base_url}. Ensure Ollama daemon is running."
            ) from exc
        except httpx.TimeoutException as exc:
            raise ProviderTimeoutError(
                f"Ollama inference timed out after {self._timeout_seconds}s for model {self._model_name}."
            ) from exc
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                raise ProviderUnavailableError(
                    f"Model '{self._model_name}' not found in Ollama. Run: ollama pull {self._model_name}"
                ) from exc
            raise ProviderError(f"Ollama returned HTTP error {exc.response.status_code}: {exc.response.text}") from exc
        except Exception as exc:
            raise ProviderError(f"Unexpected error communicating with Ollama: {str(exc)}") from exc

    async def check_availability(self) -> ProviderStatus:
        """Query Ollama daemon tags endpoint to check connectivity and model existence."""
        endpoint = f"{self._base_url}/api/tags"
        start_time = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                response = await client.get(endpoint)
                elapsed_ms = (time.perf_counter() - start_time) * 1000

                if response.status_code != 200:
                    return ProviderStatus(
                        provider_name=self.name,
                        is_available=False,
                        model_name=self._model_name,
                        latency_ms=elapsed_ms,
                        message=f"Ollama responded with HTTP {response.status_code}",
                    )

                data = response.json()
                installed_models = [
                    m.get("name", "") for m in data.get("models", [])
                ]
                # Check exact or prefix match (e.g. gemma3:1b or gemma3:1b-instruct)
                has_model = any(
                    self._model_name in m or m.startswith(self._model_name.split(":")[0])
                    for m in installed_models
                )

                return ProviderStatus(
                    provider_name=self.name,
                    is_available=True,
                    model_name=self._model_name,
                    latency_ms=round(elapsed_ms, 2),
                    message="Ollama online" if has_model else f"Ollama online, but model '{self._model_name}' not found",
                    extra_metadata={"installed_models": installed_models, "model_ready": has_model},
                )
        except Exception as exc:
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            return ProviderStatus(
                provider_name=self.name,
                is_available=False,
                model_name=self._model_name,
                latency_ms=round(elapsed_ms, 2),
                message=f"Ollama unreachable: {str(exc)}",
            )

