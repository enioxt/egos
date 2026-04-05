"""Guard Brasil + OpenAI integration

Install: pip install egosbr-guard-brasil[openai]

Usage:
    from openai import OpenAI
    from guard_brasil.integrations.openai import GuardedOpenAI

    client = GuardedOpenAI(OpenAI(), guard_api_key="gb_live_...")
    # Drop-in replacement — masks PII in messages before sending
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": "CPF 123.456.789-09..."}],
    )
"""
from __future__ import annotations
from typing import Optional
from guard_brasil import GuardBrasil


def guard_openai_messages(
    messages: list[dict],
    api_key: Optional[str] = None,
) -> list[dict]:
    """
    Mask PII in OpenAI-format messages before sending to the API.

    Args:
        messages: List of OpenAI message dicts (role/content format).
        api_key: Guard Brasil API key.

    Returns:
        New list of messages with PII masked in all string content fields.

    Example:
        safe_messages = guard_openai_messages(messages)
        response = openai_client.chat.completions.create(
            model="gpt-4o", messages=safe_messages
        )
    """
    guard = GuardBrasil(api_key=api_key)
    return [
        {**msg, "content": guard.mask(msg["content"])}
        if isinstance(msg.get("content"), str)
        else msg
        for msg in messages
    ]


class GuardedOpenAI:
    """
    Drop-in OpenAI client wrapper that automatically masks Brazilian PII
    in all outgoing messages before they reach the OpenAI API.

    Args:
        openai_client: An instantiated openai.OpenAI (or AsyncOpenAI) client.
        guard_api_key: Guard Brasil API key. Falls back to GUARD_BRASIL_API_KEY.

    Example:
        from openai import OpenAI
        from guard_brasil.integrations.openai import GuardedOpenAI

        client = GuardedOpenAI(OpenAI())
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "RG 12.345.678-9"}],
        )
        # PII is masked before hitting OpenAI — receipt available via guard.last_result
    """

    def __init__(self, openai_client, guard_api_key: Optional[str] = None):
        self._client = openai_client
        self._guard = GuardBrasil(api_key=guard_api_key)
        self.chat = self._Chat(openai_client.chat, self._guard)

    # Proxy all other attributes transparently
    def __getattr__(self, name: str):
        return getattr(self._client, name)

    class _Chat:
        def __init__(self, chat, guard: GuardBrasil):
            self.completions = self._Completions(chat.completions, guard)

        class _Completions:
            def __init__(self, completions, guard: GuardBrasil):
                self._completions = completions
                self._guard = guard

            def create(self, **kwargs):
                if "messages" in kwargs:
                    kwargs["messages"] = [
                        {**msg, "content": self._guard.mask(msg["content"])}
                        if isinstance(msg.get("content"), str)
                        else msg
                        for msg in kwargs["messages"]
                    ]
                return self._completions.create(**kwargs)

            def __getattr__(self, name: str):
                return getattr(self._completions, name)
