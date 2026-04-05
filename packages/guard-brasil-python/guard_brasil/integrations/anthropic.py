"""Guard Brasil + Anthropic integration

Install: pip install egosbr-guard-brasil[anthropic]

Usage:
    from anthropic import Anthropic
    from guard_brasil.integrations.anthropic import GuardedAnthropic

    client = GuardedAnthropic(Anthropic(), guard_api_key="gb_live_...")
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[{"role": "user", "content": "CPF 123.456.789-09..."}],
    )
"""
from __future__ import annotations
from typing import Optional
from guard_brasil import GuardBrasil


def guard_anthropic_messages(
    messages: list[dict],
    api_key: Optional[str] = None,
) -> list[dict]:
    """
    Mask PII in Anthropic-format messages before sending to the API.

    Handles both string content and list-of-blocks content format.

    Args:
        messages: List of Anthropic message dicts (role/content format).
        api_key: Guard Brasil API key.

    Returns:
        New list of messages with PII masked in all text content.
    """
    guard = GuardBrasil(api_key=api_key)

    def _mask_content(content):
        if isinstance(content, str):
            return guard.mask(content)
        if isinstance(content, list):
            return [
                {**block, "text": guard.mask(block["text"])}
                if block.get("type") == "text" and isinstance(block.get("text"), str)
                else block
                for block in content
            ]
        return content

    return [
        {**msg, "content": _mask_content(msg["content"])}
        if "content" in msg
        else msg
        for msg in messages
    ]


class GuardedAnthropic:
    """
    Drop-in Anthropic client wrapper that automatically masks Brazilian PII
    in all outgoing messages before they reach the Anthropic API.

    Args:
        anthropic_client: An instantiated anthropic.Anthropic client.
        guard_api_key: Guard Brasil API key. Falls back to GUARD_BRASIL_API_KEY.

    Example:
        from anthropic import Anthropic
        from guard_brasil.integrations.anthropic import GuardedAnthropic

        client = GuardedAnthropic(Anthropic())
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[{"role": "user", "content": "CNPJ 12.345.678/0001-99"}],
        )
        # PII removed before request leaves your server
    """

    def __init__(self, anthropic_client, guard_api_key: Optional[str] = None):
        self._client = anthropic_client
        self._guard = GuardBrasil(api_key=guard_api_key)
        self.messages = self._Messages(anthropic_client.messages, self._guard)

    def __getattr__(self, name: str):
        return getattr(self._client, name)

    class _Messages:
        def __init__(self, messages, guard: GuardBrasil):
            self._messages = messages
            self._guard = guard

        def create(self, **kwargs):
            if "messages" in kwargs:
                kwargs["messages"] = guard_anthropic_messages(
                    kwargs["messages"], api_key=self._guard.api_key
                )
            return self._messages.create(**kwargs)

        def stream(self, **kwargs):
            if "messages" in kwargs:
                kwargs["messages"] = guard_anthropic_messages(
                    kwargs["messages"], api_key=self._guard.api_key
                )
            return self._messages.stream(**kwargs)

        def __getattr__(self, name: str):
            return getattr(self._messages, name)
