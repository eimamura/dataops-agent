"""Custom LangChain tools tuned for the agent."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from langchain.tools import BaseTool

from .config import Settings


class LocalTimeTool(BaseTool):
    name: str = "get_local_time"
    description: str = (
        "Useful for answering questions that depend on the current local date and time."
    )

    def _run(self, _: str) -> str:  # type: ignore[override]
        return datetime.now().isoformat(timespec="seconds")

    async def _arun(self, _: str) -> str:  # type: ignore[override]
        return self._run("")


class NotesTool(BaseTool):
    name: str = "append_to_notes"
    description: str = (
        "Persist important discoveries about the user's data operations environment. "
        "Input should be a concise sentence you want to append to the notes file."
    )

    def __init__(self, notes_path: Path):
        super().__init__()
        self._notes_path = notes_path

    def _run(self, note: str) -> str:  # type: ignore[override]
        note = note.strip()
        if not note:
            return "No note captured (empty input)."

        self._notes_path.parent.mkdir(parents=True, exist_ok=True)
        with self._notes_path.open("a", encoding="utf-8") as handle:
            handle.write(f"{self._current_timestamp()} - {note}\n")
        return f"Captured note: {note}"

    async def _arun(self, note: str) -> str:  # type: ignore[override]
        return self._run(note)

    @staticmethod
    def _current_timestamp() -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def build_default_tools(settings: Settings) -> list[BaseTool]:
    """Return the baseline toolset used by the agent."""
    notes_path = Path(settings.notes_path)
    return [
        LocalTimeTool(),
        NotesTool(notes_path),
    ]
