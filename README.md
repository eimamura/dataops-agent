# DataOps Agent

Starter LangChain project for building task-focused AI agents that automate data operations.

## Features
- Structured settings via Pydantic.
- CLI runner powered by Typer + Rich.
- LangChain agent scaffold with pluggable tools.
- Optional SQL generation + execution tool via LangChain SQLDatabaseChain + SQLAlchemy.

## Getting Started
```bash
uv venv          # or python -m venv .venv
source .venv/bin/activate
uv pip install -e ".[dev]"  # or pip install -e ".[dev]"
cp .env.example .env
```

Configure `.env` with either your Hugging Face credentials or OpenAI credentials. Use
`LLM_PROVIDER` to toggle between the two.

To enable SQL assistance, set `DATABASE_URL` to any SQLAlchemy connection string
(e.g., `postgresql+psycopg://dataops:changeme@localhost:5432/dataops`). The agent
can then generate SQL, execute it, and summarize the result set.

## Usage
Run the CLI and start chatting with the agent:
```bash
python -m aiagent.cli "Summarize the current airflow DAG health."
```

Use `python -m aiagent.cli --help` for interactive mode and options such as enabling notes or setting temperature.

### Model Configuration
- `LLM_PROVIDER`: `huggingface` (default) or `openai`.
- `MODEL_NAME`: huggingface repo id or OpenAI model id (e.g., `meta-llama/Meta-Llama-3-8B-Instruct`, `gpt-4o-mini`).
- `HUGGINGFACE_ENDPOINT_URL`: optional; point to a private Inference Endpoint if you host your own model.
- `HUGGINGFACEHUB_API_TOKEN`: optional when using public repos but required for private endpoints.
- `OPENAI_API_KEY` / `OPENAI_API_BASE`: required when `LLM_PROVIDER=openai` (base URL only when targeting Azure or compatible endpoints).
- `MAX_NEW_TOKENS`: cap responses for predictable billing/perf.
- `DATABASE_URL`: optional SQLAlchemy connection string used by the SQL tool (Postgres example above).

## Local Postgres (Docker)
We ship a `compose.yaml` that provisions PostgreSQL 16 for local persistence and agent experimentation.

1. Create a password secret (ignored via `.gitignore`):
   ```bash
   mkdir -p .secrets
   echo 'super-strong-pass' > .secrets/postgres_password
   ```
2. Optional: adjust `POSTGRES_DB`, `POSTGRES_USER`, or `POSTGRES_PORT` in your shell before starting.
3. Launch the database:
   ```bash
   docker compose up -d postgres
   ```
4. A named volume (`postgres-data`) stores data; remove it to reset.
5. `infra/postgres/initdb.sql` seeds the `dataops` schema with `users`, `products`, and `sales` tables—edit this file to customize bootstrap data.

`pg_isready` health checks ensure the service reports healthy only after accepting connections. Connect via `psql postgres://dataops:changeme@localhost:5432/dataops`.

## Tests & Linting
```bash
pytest
ruff check .
```

## Next Steps
- Add domain-specific LangChain tools (SQL, dbt, Airflow, etc.).
- Persist agent state in your preferred store (Redis, Postgres, S3).
- Wrap the CLI with an API or workflow orchestrator.
- Experiment with different Hugging Face-hosted instruct models (Llama 3, Mixtral, Phi-3, etc.).
