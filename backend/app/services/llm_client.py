"""LLM client abstractions for Azure OpenAI."""
from __future__ import annotations

import json
from typing import Any, Dict, List, Protocol

from openai import AzureOpenAI


class LLMClient(Protocol):
    """Protocol describing LLM capabilities used by the interview service."""

    def chat_completion(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """Execute a chat completion with the given messages."""


class AzureOpenAILLM:
    """Wrapper around Azure OpenAI Chat Completions."""

    def __init__(
        self,
        *,
        api_key: str,
        endpoint: str,
        deployment: str,
        api_version: str,
        temperature: float = 0.2,
        max_tokens: int = 900,
    ) -> None:
        self._client = AzureOpenAI(
            api_key=api_key,
            azure_endpoint=endpoint,
            api_version=api_version,
        )
        self._deployment = deployment
        self._temperature = temperature
        self._max_tokens = max_tokens

    def chat_completion(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        response = self._client.chat.completions.create(
            model=self._deployment,
            messages=messages,
            temperature=self._temperature,
            max_tokens=self._max_tokens,
            response_format={"type": "json_object"},
        )
        payload = response.model_dump()
        return payload

    @staticmethod
    def extract_content(payload: Dict[str, Any]) -> Dict[str, Any]:
        """Parse the JSON content string returned by Azure."""

        try:
            choice = payload["choices"][0]
            message = choice["message"]
            content = message.get("content", "{}")
            return json.loads(content)
        except (KeyError, json.JSONDecodeError, IndexError) as exc:  # pragma: no cover - defensive
            raise ValueError("Unable to parse LLM response payload") from exc


__all__ = ["LLMClient", "AzureOpenAILLM"]
