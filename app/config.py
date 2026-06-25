from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-chat"

    database_path: str = "./data/sample.db"
    max_agent_steps: int = 5
    sql_max_rows: int = 100
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    @property
    def db_path(self) -> Path:
        return Path(self.database_path).resolve()


@lru_cache
def get_settings() -> Settings:
    return Settings()
