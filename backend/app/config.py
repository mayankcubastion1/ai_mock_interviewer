"""Application configuration utilities."""
from __future__ import annotations

from functools import lru_cache
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Runtime configuration sourced from environment variables."""

    def __init__(self) -> None:
        self.azure_openai_endpoint: Optional[str] = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.azure_openai_api_key: Optional[str] = os.getenv("AZURE_OPENAI_API_KEY")
        self.azure_openai_deployment: Optional[str] = os.getenv("AZURE_OPENAI_DEPLOYMENT")
        self.azure_openai_api_version: Optional[str] = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")
        self.cors_allow_origins: list[str] = self._parse_list(os.getenv("CORS_ALLOW_ORIGINS"))

    @staticmethod
    def _parse_list(raw: Optional[str]) -> list[str]:
        if not raw:
            return ["*"]
        return [item.strip() for item in raw.split(",") if item.strip()]

    def require_azure_config(self) -> None:
        missing = [
            name
            for name, value in (
                ("AZURE_OPENAI_ENDPOINT", self.azure_openai_endpoint),
                ("AZURE_OPENAI_API_KEY", self.azure_openai_api_key),
                ("AZURE_OPENAI_DEPLOYMENT", self.azure_openai_deployment),
            )
            if not value
        ]
        if missing:
            joined = ", ".join(missing)
            raise RuntimeError(
                "Missing Azure OpenAI configuration. Please set the following environment variables: "
                f"{joined}."
            )


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()


__all__ = ["Settings", "get_settings"]
