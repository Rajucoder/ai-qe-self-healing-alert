from __future__ import annotations

from typing import Protocol

import mlflow

from app.config.settings import Settings


class LLMProvider(Protocol):

    def complete(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        ...


class DeterministicProvider:

    @mlflow.trace(
        name="deterministic_llm_call",
        span_type="LLM",
    )
    def complete(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        return (
            "Proceed with the typed investigation workflow "
            "and report only observed results."
        )


class GroqProvider:

    def __init__(self, settings: Settings) -> None:
        from openai import OpenAI

        if not settings.groq_api_key:
            raise ValueError(
                "GROQ_API_KEY is required when "
                "LLM_PROVIDER=groq"
            )

        self._client = OpenAI(
            api_key=settings.groq_api_key,
            base_url="https://api.groq.com/openai/v1",
        )

        self._model = settings.groq_model

    @mlflow.trace(
        name="groq_llm_call",
        span_type="LLM",
    )
    def complete(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        response = self._client.chat.completions.create(
            model=self._model,
            temperature=0.1,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
        )

        return response.choices[0].message.content or ""


def build_provider(settings: Settings) -> LLMProvider:

    if settings.llm_provider == "groq":
        return GroqProvider(settings)

    if settings.llm_provider != "deterministic":
        raise ValueError(
            f"Unsupported LLM_PROVIDER: {settings.llm_provider}"
        )

    return DeterministicProvider()