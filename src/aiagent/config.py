"""Configuration helpers."""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralized runtime settings."""

    model_config = SettingsConfigDict(env_file=(".env",), env_file_encoding="utf-8", extra="ignore")

    openai_api_key: str = Field(..., alias="OPENAI_API_KEY")
    openai_base_url: str | None = Field(default=None, alias="OPENAI_BASE_URL")
    model_name: str = Field(default="gpt-4o-mini", alias="MODEL_NAME")
    temperature: float = 0.0
    agent_mode: Literal["react", "conversational"] = "react"
    verbose: bool = Field(default=False, alias="AGENT_VERBOSITY")
    notes_path: str = "notes.md"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Singleton accessor for settings."""
    return Settings()
