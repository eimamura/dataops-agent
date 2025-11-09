"""LangChain agent factory."""

from __future__ import annotations

from typing import Final

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint

from .config import Settings
from .tools import build_default_tools

REACT_SYSTEM_PROMPT: Final[str] = (
    "You are a focused data-operations copilot. "
    "Think step-by-step, citing the reasoning that leads you to call the available tools. "
    "Prefer tool output over assumptions whenever data is required."
)
CONVERSATIONAL_SYSTEM_PROMPT: Final[str] = (
    "You are a personable data-operations copilot. "
    "Maintain awareness of conversation history, explain your reasoning, "
    "and call the provided tools for any factual lookup or note taking."
)
SYSTEM_PROMPTS: Final[dict[str, str]] = {
    "react": REACT_SYSTEM_PROMPT,
    "conversational": CONVERSATIONAL_SYSTEM_PROMPT,
}


def _sanitize_env_value(raw_value: str | None) -> str | None:
    """Trim whitespace/comment-only env values so config is easier to manage."""
    if not raw_value:
        return None
    cleaned = raw_value.strip()
    if not cleaned or cleaned.startswith("#"):
        return None
    return cleaned


def _build_text_model(settings: Settings) -> HuggingFaceEndpoint:
    """Return the base text-generation LLM used by the chat wrapper."""
    base_kwargs = {
        "huggingfacehub_api_token": settings.hf_api_token,
        "max_new_tokens": settings.max_new_tokens,
        "temperature": settings.temperature,
    }
    endpoint_url = _sanitize_env_value(settings.hf_endpoint_url)
    if endpoint_url:
        return HuggingFaceEndpoint(
            endpoint_url=endpoint_url,
            **base_kwargs,
        )
    return HuggingFaceEndpoint(
        repo_id=settings.model_name,
        **base_kwargs,
    )


def _build_openai_chat_model(settings: Settings) -> ChatOpenAI:
    """Return a ChatOpenAI instance configured from the Settings."""
    api_key = _sanitize_env_value(settings.openai_api_key)
    if not api_key:
        raise ValueError("OPENAI_API_KEY must be set when LLM_PROVIDER=openai.")

    init_kwargs: dict[str, object] = {
        "model": settings.model_name,
        "temperature": settings.temperature,
        "max_tokens": settings.max_new_tokens,
        "api_key": api_key,
    }
    base_url = _sanitize_env_value(settings.openai_base_url)
    if base_url:
        init_kwargs["base_url"] = base_url
    return ChatOpenAI(**init_kwargs)


def _build_chat_model(settings: Settings):
    """Dispatch to the correct chat model based on configuration."""
    provider = settings.llm_provider.lower()
    if provider == "openai":
        return _build_openai_chat_model(settings)
    if provider == "huggingface":
        return ChatHuggingFace(llm=_build_text_model(settings))
    raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}")


def _system_prompt(mode: str) -> str:
    """Return the system prompt associated with the configured mode."""
    return SYSTEM_PROMPTS.get(mode, REACT_SYSTEM_PROMPT)


def _build_agent_prompt(system_prompt: str) -> ChatPromptTemplate:
    """Prompt template that threads history + scratchpad."""
    return ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="messages", optional=True),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )


def build_agent(settings: Settings) -> AgentExecutor:
    """Construct the LangChain agent executor."""
    chat_llm = _build_chat_model(settings)

    tools = build_default_tools(settings, chat_llm)
    prompt = _build_agent_prompt(_system_prompt(settings.agent_mode))
    agent_runnable = create_tool_calling_agent(chat_llm, tools, prompt)
    return AgentExecutor(
        agent=agent_runnable,
        tools=tools,
        verbose=settings.verbose,
    )
