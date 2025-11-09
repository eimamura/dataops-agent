"""Configuration helpers."""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralized runtime settings."""

    model_config = SettingsConfigDict(env_file=(".env",), env_file_encoding="utf-8", extra="ignore")

    hf_api_token: str | None = Field(default=None, alias="HUGGINGFACEHUB_API_TOKEN")
    hf_endpoint_url: str | None = Field(default=None, alias="HUGGINGFACE_ENDPOINT_URL")
    model_name: str = Field(default="meta-llama/Meta-Llama-3-8B-Instruct", alias="MODEL_NAME")
    max_new_tokens: int = Field(default=512, alias="MAX_NEW_TOKENS")
    temperature: float = 0.0
    agent_mode: Literal["react", "conversational"] = "react"
    verbose: bool = Field(default=False, alias="AGENT_VERBOSITY")
    llm_provider: Literal["huggingface", "openai"] = Field(default="huggingface", alias="LLM_PROVIDER")
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    openai_base_url: str | None = Field(default=None, alias="OPENAI_API_BASE")
    notes_path: str = "notes.md"
    database_url: str | None = Field(default=None, alias="DATABASE_URL")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Singleton accessor for settings."""
    return Settings()
