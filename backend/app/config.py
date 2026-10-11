"""Configuration settings for GreenQuest backend."""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable overrides."""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:4173,https://greenquest.onrender.com,*"

    # Provider settings: "ollama", "fallback", "hosted"
    MODEL_PROVIDER: str = "ollama"
    FORCE_FALLBACK: bool = False

    # Ollama settings (Gemma 3 1B)
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "gemma3:1b"
    OLLAMA_TIMEOUT_SECONDS: float = 25.0

    # Optional Hosted Provider settings
    HOSTED_API_BASE_URL: str = "https://api.together.xyz/v1"
    HOSTED_API_KEY: str = ""
    HOSTED_MODEL: str = "google/gemma-3-1b-it"

    # Orchestrator settings
    MAX_SAFETY_RETRIES: int = 2
    LOG_LEVEL: str = "INFO"

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins string to list."""
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


settings = Settings()

