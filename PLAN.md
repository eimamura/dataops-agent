# DataOps Agent Implementation Plan

## Phase 1: Read-Only SQL Guard

Goal: make the existing SQL tool safe enough to use as a read-only analytics assistant.

1. Add a read-only SQL validation layer to `SQLQueryTool`.
   - Accept direct SQL and LLM-generated SQL only after validation.
   - Treat `SELECT` as the primary allowed statement type.
   - Treat `WITH` cautiously because Postgres supports writable CTEs.
   - Reject obvious write or schema-changing statements such as `INSERT`, `UPDATE`, `DELETE`, `CREATE`, `DROP`, `ALTER`, `TRUNCATE`, `CALL`, and `MERGE`.
   - Reject multiple statements in one tool call.

2. Add focused tests under `tests/`.
   - SQL extraction from plain SQL, fenced SQL, and LLM-style labels.
   - Rejection of direct write statements.
   - Rejection of LLM-generated write statements.
   - Rejection of writable CTE examples.
   - Rejection of multiple statements.
   - Coverage for comments and strings so the current conservative behavior is explicit.

3. Update user-facing documentation.
   - State that SQL support is read-only by default.
   - Recommend using a read-only DB user for `DATABASE_URL` in production or shared environments.
   - Clarify that application-level SQL validation is a guardrail, not a substitute for database permissions.

## Phase 1.5: SQL Dependency Cleanup

Goal: remove setup ambiguity without delaying the read-only guard.

1. Align SQL dependencies.
   - Decide whether to add `langchain-classic` directly or document it as an optional SQL dependency.
   - Ensure README setup instructions match the actual behavior when `DATABASE_URL` is set.

2. Clean `.env.example`.
   - Avoid inline comments in environment values.
   - Make the read-only DB user recommendation visible near `DATABASE_URL`.

## Phase 2: Practical Query Execution

Goal: make query execution predictable and auditable.

1. Add configurable result limits.
2. Record executed SQL, execution duration, row count, and errors.
3. Return concise summaries for large result sets.
4. Keep structured execution logs separate from free-form `notes.md`.

## Phase 3: Schema Exploration

Goal: reduce LLM guessing before SQL generation.

1. Add a table listing tool.
2. Add table detail output for columns, types, foreign keys, and sample rows.
3. Update the agent prompt to prefer schema exploration before generating SQL.

## Phase 4: DataOps Operations

Goal: expand from analytics assistance to operational visibility.

1. Add read-only dbt manifest and run result tools.
2. Add read-only Airflow or Dagster status tools.
3. Defer reruns and write operations until explicit confirmation, permissions, and audit logging are designed.

## Deferred Decisions

- Whether to introduce `sqlglot` or another SQL parser for robust read-only validation.
- Whether local `compose.yaml` should create a dedicated read-only analytics user.
- Whether notes, conversation history, and SQL execution history should share a SQLite or Postgres-backed session store.
