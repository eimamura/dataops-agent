"""Custom LangChain tools tuned for the agent."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from langchain_core.language_models import BaseLanguageModel
from langchain_core.tools import BaseTool
from langchain_community.utilities import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain
from sqlalchemy.exc import SQLAlchemyError

from .config import Settings


class LocalTimeTool(BaseTool):
    name: str = "get_local_time"
    description: str = (
        "Useful for answering questions that depend on the current local date and time."
    )

    def _run(self, _: str | None = None) -> str:  # type: ignore[override]
        return datetime.now().isoformat(timespec="seconds")

    async def _arun(self, _: str | None = None) -> str:  # type: ignore[override]
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


class SQLQueryTool(BaseTool):
    name: str = "query_sql_database"
    description: str = (
        "Generate SQL from natural language, execute it against the configured database, "
        "and return concise results. Provide the analytics question or the SQL to run."
    )

    def __init__(self, sql_chain: SQLDatabaseChain):
        super().__init__()
        self._sql_chain = sql_chain

    def _run(self, instructions: str) -> str:  # type: ignore[override]
        question = instructions.strip()
        if not question:
            return "Provide a natural-language question or SQL statement to execute."
        return self._sql_chain.invoke(question)

    async def _arun(self, instructions: str) -> str:  # type: ignore[override]
        question = instructions.strip()
        if not question:
            return "Provide a natural-language question or SQL statement to execute."
        return await self._sql_chain.ainvoke(question)


def build_default_tools(settings: Settings, llm: BaseLanguageModel | None = None) -> list[BaseTool]:
    """Return the baseline toolset used by the agent."""
    notes_path = Path(settings.notes_path)
    tools: list[BaseTool] = [
        LocalTimeTool(),
        NotesTool(notes_path),
    ]
    sql_tool = _build_sql_tool(settings, llm)
    if sql_tool:
        tools.append(sql_tool)
    return tools


def _build_sql_tool(settings: Settings, llm: BaseLanguageModel | None) -> BaseTool | None:
    database_url = (settings.database_url or "").strip()
    if not database_url or llm is None:
        return None

    try:
        database = SQLDatabase.from_uri(database_url)
    except SQLAlchemyError as exc:  # pragma: no cover - configuration feedback
        raise RuntimeError(f"Failed to connect to SQL database: {exc}") from exc

    sql_chain = SQLDatabaseChain.from_llm(
        llm=llm,
        db=database,
        verbose=settings.verbose,
        use_query_checker=True,
    )
    return SQLQueryTool(sql_chain)
