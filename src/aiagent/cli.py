"""Command line runner for the LangChain agent."""

from __future__ import annotations

from typing import Any, Optional

import typer
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
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
    conversation: list[BaseMessage] = []

    if prompt:
        _run_once(agent, prompt, conversation)
        return

    if not interactive:
        interactive = True

    console.print("[bold green]Interactive agent mode. Type 'exit' to quit.[/]")
    while interactive:
        user_input = Prompt.ask("[cyan]You[/]").strip()
        if user_input.lower() in {"exit", "quit"}:
            console.print("[yellow]Goodbye![/]")
            break
        _run_once(agent, user_input, conversation)


def _run_once(agent, user_input: str, conversation: list[BaseMessage]) -> None:
    user_message = HumanMessage(content=user_input)
    conversation.append(user_message)
    try:
        response = agent.invoke({"messages": conversation})
    except Exception as exc:  # pragma: no cover - surface to CLI
        conversation.pop()  # roll back user message in history
        console.print(f"[red]Agent failed:[/] {exc}")
        return

    output_text = _extract_text_response(response)
    conversation.append(AIMessage(content=output_text))
    console.print(f"[magenta]Agent:[/] {output_text}")


def _extract_text_response(response: Any) -> str:
    """Coerce the agent response into printable text."""
    if isinstance(response, dict):
        output = response.get("output")
        if isinstance(output, str) and output.strip():
            return output
        messages = response.get("messages")
        if isinstance(messages, list) and messages:
            message = messages[-1]
            content = getattr(message, "content", None)
            if isinstance(content, str):
                return content
            if isinstance(content, list):
                parts = [
                    chunk.get("text", "")
                    for chunk in content
                    if isinstance(chunk, dict) and chunk.get("type") == "text"
                ]
                text = "\n".join(part for part in parts if part)
                if text:
                    return text
            if isinstance(message, dict):
                text = message.get("content")
                if isinstance(text, str):
                    return text
    return str(response)


if __name__ == "__main__":
    typer.run(main)
