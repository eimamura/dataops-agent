# DataOps Agent

Starter LangChain project for building task-focused AI agents that automate data operations.

## Features
- Structured settings via Pydantic.
- CLI runner powered by Typer + Rich.
- LangChain agent scaffold with pluggable tools.

## Getting Started
```bash
uv venv          # or python -m venv .venv
source .venv/bin/activate
uv pip install -e ".[dev]"  # or pip install -e ".[dev]"
cp .env.example .env
```

Supply your OpenAI API key (or compatible endpoint) by editing `.env`.

## Usage
Run the CLI and start chatting with the agent:
```bash
python -m aiagent.cli "Summarize the current airflow DAG health."
```

Use `python -m aiagent.cli --help` for interactive mode and options such as enabling notes or setting temperature.

## Tests & Linting
```bash
pytest
ruff check .
```

## Next Steps
- Add domain-specific LangChain tools (SQL, dbt, Airflow, etc.).
- Persist agent state in your preferred store (Redis, Postgres, S3).
- Wrap the CLI with an API or workflow orchestrator.
