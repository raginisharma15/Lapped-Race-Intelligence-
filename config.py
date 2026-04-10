from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application runtime settings loaded from environment variables."""

    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"
    openf1_base_url: str = "https://api.openf1.org/v1"
    fastf1_cache_dir: str = "./cache/fastf1"
    default_session_key: str = "latest"
    alert_buffer_size: int = 50
    anomaly_threshold: float = 0.15

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached settings instance."""
    return Settings()
