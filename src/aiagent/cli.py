"""Command line runner for the LangChain agent."""

from __future__ import annotations

from typing import Any, Optional

import typer
from langchain_core.messages import AIMessage, HumanMessage
from rich.console import Console
from rich.prompt import Prompt

from .agent import build_agent
from .config import Settings, get_settings

console = Console()


def _resolve_settings(verbose_flag: bool) -> Settings:
    base = get_settings()
    if verbose_flag and not base.verbose:
        return base.model_copy(update={"verbose": True})
    return base


def main(
    prompt: Optional[str] = typer.Argument(None, help="Optional one-shot prompt."),
    interactive: bool = typer.Option(
        False,
        "--interactive",
        "-i",
        help="Start an interactive loop (default when no prompt is supplied).",
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable LangChain verbose logs."),
) -> None:
    """Execute the LangChain agent."""
    settings = _resolve_settings(verbose)
    agent = build_agent(settings)
    state: dict[str, Any] = {"messages": []}

    if prompt:
        _run_once(agent, prompt, state)
        return

    if not interactive:
        interactive = True

    console.print("[bold green]Interactive agent mode. Type 'exit' to quit.[/]")
    while interactive:
        user_input = Prompt.ask("[cyan]You[/]").strip()
        if user_input.lower() in {"exit", "quit"}:
            console.print("[yellow]Goodbye![/]")
            break
        _run_once(agent, user_input, state)


def _run_once(agent, user_input: str, state: dict[str, Any]) -> None:
    prior_messages = state.get("messages") or []
    new_messages = list(prior_messages)
    new_messages.append(HumanMessage(content=user_input))
    try:
        response = agent.invoke({"messages": new_messages})
    except Exception as exc:  # pragma: no cover - surface to CLI
        console.print(f"[red]Agent failed:[/] {exc}")
        return

    response_messages = _extract_messages(response)
    if response_messages is None:
        output_text = _extract_text_response(response, new_messages)
        response_messages = [*new_messages, AIMessage(content=output_text)]
    else:
        output_text = _extract_text_response(response, response_messages)

    state["messages"] = response_messages
    console.print(f"[magenta]Agent:[/] {output_text}")


def _extract_messages(response: Any) -> list[Any] | None:
    """Return the messages payload emitted by the agent if present."""
    if isinstance(response, dict):
        messages = response.get("messages")
        if isinstance(messages, list):
            return messages
    if isinstance(response, list):
        return response
    return None


def _extract_text_response(response: Any, messages: list[Any] | None = None) -> str:
    """Coerce the agent response into printable text."""
    candidates = messages or _extract_messages(response) or []
    for message in reversed(candidates):
        text = _message_text(message)
        if text:
            return text
    if isinstance(response, dict):
        output = response.get("output")
        if isinstance(output, str) and output.strip():
            return output.strip()
    return str(response)


def _message_text(message: Any) -> str | None:
    """Extract assistant text from a LangChain message-like object."""
    role = getattr(message, "type", None)
    content = getattr(message, "content", None)
    if isinstance(message, dict):
        role = message.get("role") or message.get("type")
        content = message.get("content")

    if role not in {"ai", "assistant", "assistant_message"}:
        return None

    if isinstance(content, str):
        text = content.strip()
        return text or None

    if isinstance(content, list):
        parts = []
        for chunk in content:
            if isinstance(chunk, dict) and chunk.get("type") == "text":
                text = chunk.get("text")
                if isinstance(text, str) and text.strip():
                    parts.append(text.strip())
        if parts:
            return "\n".join(parts)
    return None


if __name__ == "__main__":
    typer.run(main)
