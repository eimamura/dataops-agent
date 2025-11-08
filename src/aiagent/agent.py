"""LangChain agent factory."""

from langchain.agents import AgentExecutor, AgentType, initialize_agent
from langchain_openai import ChatOpenAI

from .config import Settings
from .tools import build_default_tools


def build_agent(settings: Settings) -> AgentExecutor:
    """Construct the LangChain agent executor."""
    llm = ChatOpenAI(
        model=settings.model_name,
        temperature=settings.temperature,
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
    )

    tools = build_default_tools(settings)
    agent_type = (
        AgentType.ZERO_SHOT_REACT_DESCRIPTION
        if settings.agent_mode == "react"
        else AgentType.CONVERSATIONAL_REACT_DESCRIPTION
    )

    return initialize_agent(
        tools=tools,
        llm=llm,
        agent=agent_type,
        verbose=settings.verbose,
        handle_parsing_errors=True,
    )
