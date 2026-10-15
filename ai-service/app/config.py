from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(REPO_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    anthropic_api_key: str = ""
    llm_model: str = "claude-sonnet-5-5"
    llm_max_tokens: int = 1024
    retrieval_top_k: int = 8
    abstention_threshold: float = 0.5
    ai_service_port: int = 8000


settings = Settings()


def safe_config() -> dict:
    """Non-secret config exposed via GET /config. Never include the API key."""
    return {
        "llm_model": settings.llm_model,
        "llm_max_tokens": settings.llm_max_tokens,
        "retrieval_top_k": settings.retrieval_top_k,
        "abstention_threshold": settings.abstention_threshold,
    }
