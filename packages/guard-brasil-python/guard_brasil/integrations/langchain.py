"""Guard Brasil + LangChain integration

Install: pip install egosbr-guard-brasil[langchain]

Usage:
    from guard_brasil.integrations.langchain import create_guard_runnable

    guard_step = create_guard_runnable(api_key="gb_live_...")
    chain = prompt | llm | guard_step | output_parser
"""
from __future__ import annotations
from typing import Optional
from guard_brasil import GuardBrasil


def create_guard_runnable(api_key: Optional[str] = None):
    """
    Creates a LangChain-compatible Runnable that masks Brazilian PII.

    The runnable accepts a string (or AIMessage with .content) and returns
    the masked text as a string.

    Args:
        api_key: Guard Brasil API key. Falls back to GUARD_BRASIL_API_KEY env var.

    Returns:
        RunnableLambda that can be chained with | operator.

    Example:
        guard = create_guard_runnable()
        safe_text = guard.invoke("O CPF 123.456.789-09 do usuário...")
    """
    try:
        from langchain_core.runnables import RunnableLambda
        from langchain_core.messages import BaseMessage
    except ImportError:
        raise ImportError(
            "LangChain integration requires langchain-core. "
            "Install with: pip install egosbr-guard-brasil[langchain]"
        )

    guard = GuardBrasil(api_key=api_key)

    def _mask(input_: str | BaseMessage) -> str:
        text = input_.content if isinstance(input_, BaseMessage) else str(input_)
        return guard.mask(text)

    return RunnableLambda(_mask)


def create_guard_output_parser(api_key: Optional[str] = None):
    """
    Returns a LangChain BaseLLMOutputParser that strips PII from LLM output
    before it leaves the chain. Compatible with LCEL .pipe() chains.

    Example:
        chain = ChatOpenAI() | create_guard_output_parser()
        safe_response = chain.invoke([HumanMessage(content="...")])
    """
    try:
        from langchain_core.output_parsers import StrOutputParser
        from langchain_core.messages import BaseMessage
    except ImportError:
        raise ImportError(
            "Install with: pip install egosbr-guard-brasil[langchain]"
        )

    guard = GuardBrasil(api_key=api_key)
    base_parser = StrOutputParser()

    def _parse_and_guard(output) -> str:
        text = base_parser.invoke(output) if isinstance(output, BaseMessage) else str(output)
        return guard.mask(text)

    from langchain_core.runnables import RunnableLambda
    return RunnableLambda(_parse_and_guard)
