from functools import lru_cache
from typing import Literal

from pydantic import AmqpDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    BROKER_URL: AmqpDsn
    BROKER_EXCHANGE: str
    BROKER_QUEUE: str | None
    BROKER_ROUTING_KEYS_CONSUME_FROM: list[str]
    WEBSOCKETS_HOST: str
    WEBSOCKETS_PORT: int
    WEBSOCKETS_PATH: str

    AUTH_JWKS_URL: str
    AUTH_SUPPORTED_SIGNING_ALGORITHMS: list[str]

    DEBUG: bool = False
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "WARNING"
    ENVIRONMENT: str = "unknown"
    SENTRY_DSN: str | None = None
    SENTRY_TRACES_SAMPLE_RATE: float = 0.1

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


@lru_cache
def get_app_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
