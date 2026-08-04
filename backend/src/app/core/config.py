"""Application configuration using environment-based settings (12-factor)."""
from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central application settings, loaded from environment variables / .env file.

    Never hard-code secrets here; only defaults safe for local development.
    """

    model_config = SettingsConfigDict(env_file=".env", env_prefix="APP_", extra="ignore")

    environment: Literal["local", "test", "staging", "production"] = "local"
    debug: bool = False

    project_name: str = "Schedule FSI/A3 Tax Filing API"
    api_v1_prefix: str = "/api/v1"

    # SQLite for local dev, PostgreSQL for staging/production.
    database_url: str = "sqlite+aiosqlite:///./schedule_tax.db"
    database_echo: bool = False

    # Secrets management: in production these MUST be injected via environment
    # variables / a secrets manager (Vault, AWS Secrets Manager, etc.), never committed.
    secret_key: str = Field(default="change-me-in-production-please")
    csrf_secret: str = Field(default="change-me-csrf-secret")

    cors_allow_origins: list[str] = ["http://localhost:5173"]

    rate_limit_default: str = "100/minute"

    export_dir: str = "./exports"

    log_level: str = "INFO"
    log_json: bool = False

    # Selects which market-data provider the calculation engine uses for
    # Form A3 valuations when a caller does not supply explicit rates.
    market_data_provider: Literal["manual", "yfinance_sbi"] = "yfinance_sbi"
    sbi_pdf_dir: str = "../../sbi-fx-ratekeeper/pdf_files"


@lru_cache
def get_settings() -> Settings:
    return Settings()
