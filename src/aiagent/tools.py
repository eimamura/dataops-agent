"""Custom LangChain tools tuned for the agent."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import re
from typing import Any, Callable
from langchain_core.language_models import BaseLanguageModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import BaseTool
from langchain_community.utilities import SQLDatabase
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


SQL_ANSWER_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You answer analytics questions by looking at the executed SQL and its results. "
            "Always cite numbers from the result set, print the exact SQL query that was executed, "
            "and explain when no rows are returned.",
        ),
        (
            "human",
            "Question: {question}\nSQL query: {sql_query}\nSQL result: {sql_result}\nAnswer concisely.",
        ),
    ]
)


class SQLQueryTool(BaseTool):
    name: str = "query_sql_database"
    description: str = (
        "Generate SQL from natural language, execute it against the configured database, "
        "and return concise results. Provide the analytics question or the SQL to run."
    )

    def __init__(
        self,
        sql_generator,
        database: SQLDatabase,
        answer_chain,
    ) -> None:
        super().__init__()
        self._sql_generator = sql_generator
        self._database = database
        self._answer_chain = answer_chain

    def _run(self, instructions: str) -> str:  # type: ignore[override]
        question = instructions.strip()
        if not question:
            return "Provide a natural-language question or SQL statement to execute."

        direct_sql = _extract_sql_statement(question, require_leading_keyword=True)
        if direct_sql:
            sql_query = direct_sql
        else:
            try:
                generated_sql = self._sql_generator.invoke({"question": question})
            except Exception as exc:  # pragma: no cover - LLM failures
                return f"Failed to generate SQL: {exc}"

            sql_query = _extract_sql_statement(generated_sql)
            if not sql_query:
                return f"Failed to parse SQL from generator output: {generated_sql}"

        try:
            raw_result = self._database.run(sql_query)
        except SQLAlchemyError as exc:  # pragma: no cover - configuration feedback
            raise RuntimeError(f"Failed to execute SQL query: {exc}") from exc

        sql_result = raw_result if isinstance(raw_result, str) else repr(raw_result)
        try:
            return self._answer_chain.invoke(
                {
                    "question": question,
                    "sql_query": sql_query,
                    "sql_result": sql_result,
                }
            )
        except Exception:  # pragma: no cover - answer LLM failures
            return f"Query succeeded. SQL: {sql_query}. Result: {sql_result}"

    async def _arun(self, instructions: str) -> str:  # type: ignore[override]
        return self._run(instructions)


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

    create_sql_query_chain = _resolve_sql_chain_factory()
    if create_sql_query_chain is None:
        raise RuntimeError(
            "SQL support requires the legacy chains package. "
            "Install `langchain-classic` or pin langchain<1.0, or unset DATABASE_URL."
        )

    sql_generator = create_sql_query_chain(llm, database)
    answer_chain = SQL_ANSWER_PROMPT | llm | StrOutputParser()
    return SQLQueryTool(sql_generator, database, answer_chain)


def _resolve_sql_chain_factory() -> Callable | None:
    """Import create_sql_query_chain from the available LangChain distribution."""
    try:
        from langchain.chains import create_sql_query_chain  # type: ignore[import-not-found]

        return create_sql_query_chain
    except ModuleNotFoundError:
        try:
            from langchain_classic.chains import create_sql_query_chain  # type: ignore[import-not-found]

            return create_sql_query_chain
        except ModuleNotFoundError:
            return None


SQL_START_PATTERN = re.compile(
    r"\b(SELECT|WITH|INSERT|UPDATE|DELETE|CREATE|DROP|ALTER|CALL|DESCRIBE|SHOW)\b",
    re.IGNORECASE,
)


def _extract_sql_statement(candidate: Any, *, require_leading_keyword: bool = False) -> str | None:
    """Attempt to pull a runnable SQL statement from varied LLM outputs."""
    text: str | None = None
    if isinstance(candidate, dict):
        for key in ("sql_query", "sql", "query", "result"):
            value = candidate.get(key)
            if isinstance(value, str) and value.strip():
                text = value
                break
        if text is None:
            return None
    elif isinstance(candidate, str):
        text = candidate
    elif candidate is None:
        return None
    else:
        text = str(candidate)

    text = text.strip()
    if not text:
        return None

    text = _strip_code_fence(text)

    lowered = text.lower()
    for marker in ("sqlquery:", "sql query:", "sql:", "generated sql:", "query:"):
        idx = lowered.find(marker)
        if idx != -1:
            text = text[idx + len(marker) :].strip()
            lowered = text.lower()
            break

    if lowered.startswith("question:"):
        newline = text.find("\n")
        if newline != -1:
            text = text[newline + 1 :].strip()
            lowered = text.lower()

    text = _strip_code_fence(text)
    match = SQL_START_PATTERN.search(text)
    if not match:
        return None

    prefix = text[: match.start()]
    if require_leading_keyword and prefix.strip():
        return None

    sql = text[match.start() :].strip()
    sql = sql.split("```", 1)[0].strip()
    return sql or None


def _strip_code_fence(text: str) -> str:
    """Remove Markdown ``` fences if present."""
    stripped = text.strip()
    if not stripped.startswith("```"):
        return stripped

    lines = stripped.split("\n")
    if lines:
        # Drop ``` or ```sql header
        lines = lines[1:]
    cleaned = "\n".join(lines)
    if "```" in cleaned:
        cleaned = cleaned.rsplit("```", 1)[0]
    return cleaned.strip()
