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

Configure `.env` with either your Hugging Face credentials or OpenAI credentials. Use
`LLM_PROVIDER` to toggle between the two.

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
