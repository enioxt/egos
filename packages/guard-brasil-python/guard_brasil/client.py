"""
Guard Brasil Python SDK
Brazilian PII detection and LGPD compliance

Usage:
    from guard_brasil import GuardBrasil

    guard = GuardBrasil(api_key="gb_live_...")
    result = guard.inspect("O CPF 123.456.789-09 do cliente...")
    print(result.output)  # "O CPF [CPF REMOVIDO] do cliente..."
    print(result.pii_found)  # ["cpf"]
"""

from __future__ import annotations
import httpx
from dataclasses import dataclass, field
from typing import Optional
import os


API_BASE = "https://guard.egos.ia.br"


@dataclass
class PIIFinding:
    category: str
    label: str
    suggestion: str


@dataclass
class InspectionReceipt:
    inspected_at: str
    input_hash: str
    output_hash: str
    inspection_hash: str
    guard_version: str


@dataclass
class GuardResult:
    safe: bool
    blocked: bool
    output: str
    summary: str
    lgpd_disclosure: Optional[str]
    pii_found: list[str]
    findings: list[PIIFinding]
    receipt: Optional[InspectionReceipt]
    atrian_score: Optional[int]
    duration_ms: Optional[float]
    remaining_quota: Optional[int]

    @property
    def has_pii(self) -> bool:
        return len(self.findings) > 0


class GuardBrasil:
    """
    Guard Brasil — Brazilian PII detection client

    Args:
        api_key: Your Guard Brasil API key (get free at guard.egos.ia.br)
        timeout: Request timeout in seconds (default: 10)
        base_url: API base URL (default: https://guard.egos.ia.br)

    Example:
        guard = GuardBrasil(api_key="gb_live_...")
        result = guard.inspect("CPF 123.456.789-09")
        if result.has_pii:
            safe_text = result.output
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        timeout: float = 10.0,
        base_url: str = API_BASE,
    ):
        self.api_key = api_key or os.environ.get("GUARD_BRASIL_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Guard Brasil API key required. "
                "Set GUARD_BRASIL_API_KEY env var or pass api_key=..."
            )
        self.base_url = base_url
        self._client = httpx.Client(
            base_url=base_url,
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=timeout,
        )

    def inspect(self, text: str) -> GuardResult:
        """
        Inspect text for Brazilian PII and mask it.

        Args:
            text: Text to inspect (any language, works best with PT-BR)

        Returns:
            GuardResult with .output (masked text), .pii_found, .receipt

        Raises:
            httpx.HTTPStatusError: On API error (401, 429, 500)
        """
        response = self._client.post("/v1/inspect", json={"text": text})
        response.raise_for_status()
        data = response.json()

        findings = [
            PIIFinding(
                category=f["category"],
                label=f["label"],
                suggestion=f["suggestion"],
            )
            for f in (data.get("masking", {}).get("findings") or [])
        ]

        receipt_data = data.get("receipt")
        receipt = InspectionReceipt(
            inspected_at=receipt_data["inspectedAt"],
            input_hash=receipt_data["inputHash"],
            output_hash=receipt_data["outputHash"],
            inspection_hash=receipt_data["inspectionHash"],
            guard_version=receipt_data["guardVersion"],
        ) if receipt_data else None

        return GuardResult(
            safe=data.get("safe", True),
            blocked=data.get("blocked", False),
            output=data.get("output", text),
            summary=data.get("summary", ""),
            lgpd_disclosure=data.get("lgpdDisclosure"),
            pii_found=data.get("pii_found") or [f.category for f in findings],
            findings=findings,
            receipt=receipt,
            atrian_score=data.get("atrian", {}).get("score"),
            duration_ms=data.get("meta", {}).get("durationMs"),
            remaining_quota=data.get("remainingQuota"),
        )

    def mask(self, text: str) -> str:
        """Shorthand — returns only the masked text string."""
        return self.inspect(text).output

    def is_safe(self, text: str) -> bool:
        """Returns True if no PII found."""
        return self.inspect(text).safe

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self._client.close()


class AsyncGuardBrasil(GuardBrasil):
    """Async version using httpx.AsyncClient"""

    def __init__(self, *args, **kwargs):
        api_key = kwargs.get("api_key") or (args[0] if args else None)
        api_key = api_key or os.environ.get("GUARD_BRASIL_API_KEY")
        if not api_key:
            raise ValueError("Guard Brasil API key required.")
        self.api_key = api_key
        self.base_url = kwargs.get("base_url", API_BASE)
        self._async_client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=kwargs.get("timeout", 10.0),
        )

    async def inspect(self, text: str) -> GuardResult:  # type: ignore[override]
        response = await self._async_client.post("/v1/inspect", json={"text": text})
        response.raise_for_status()
        data = response.json()

        findings = [
            PIIFinding(category=f["category"], label=f["label"], suggestion=f["suggestion"])
            for f in (data.get("masking", {}).get("findings") or [])
        ]

        receipt_data = data.get("receipt")
        receipt = InspectionReceipt(
            inspected_at=receipt_data["inspectedAt"],
            input_hash=receipt_data["inputHash"],
            output_hash=receipt_data["outputHash"],
            inspection_hash=receipt_data["inspectionHash"],
            guard_version=receipt_data["guardVersion"],
        ) if receipt_data else None

        return GuardResult(
            safe=data.get("safe", True),
            blocked=data.get("blocked", False),
            output=data.get("output", text),
            summary=data.get("summary", ""),
            lgpd_disclosure=data.get("lgpdDisclosure"),
            pii_found=data.get("pii_found") or [f.category for f in findings],
            findings=findings,
            receipt=receipt,
            atrian_score=data.get("atrian", {}).get("score"),
            duration_ms=data.get("meta", {}).get("durationMs"),
            remaining_quota=data.get("remainingQuota"),
        )

    async def mask(self, text: str) -> str:  # type: ignore[override]
        return (await self.inspect(text)).output

    async def is_safe(self, text: str) -> bool:  # type: ignore[override]
        return (await self.inspect(text)).safe

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self._async_client.aclose()
