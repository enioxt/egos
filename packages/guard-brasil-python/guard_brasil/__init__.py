"""
Guard Brasil Python SDK
Brazilian PII detection and LGPD compliance

Quick start:
    from guard_brasil import GuardBrasil

    guard = GuardBrasil(api_key="gb_live_...")          # or set GUARD_BRASIL_API_KEY
    result = guard.inspect("CPF 123.456.789-09")
    print(result.output)       # masked text
    print(result.pii_found)    # ["cpf"]
    print(result.has_pii)      # True
    print(result.receipt)      # InspectionReceipt with audit hashes

Async:
    from guard_brasil import AsyncGuardBrasil

    async with AsyncGuardBrasil() as guard:
        result = await guard.inspect("...")

Integrations (install extras first):
    pip install egosbr-guard-brasil[langchain]
    pip install egosbr-guard-brasil[openai]
    pip install egosbr-guard-brasil[anthropic]
    pip install egosbr-guard-brasil[all]
"""

from .client import (
    GuardBrasil,
    AsyncGuardBrasil,
    GuardResult,
    PIIFinding,
    InspectionReceipt,
    API_BASE,
)

__version__ = "0.1.0"
__all__ = [
    "GuardBrasil",
    "AsyncGuardBrasil",
    "GuardResult",
    "PIIFinding",
    "InspectionReceipt",
    "API_BASE",
]
