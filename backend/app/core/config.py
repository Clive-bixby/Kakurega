from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field(default="Kakurega API")
    environment: str = Field(default="development")
    debug: bool = Field(default=True)
    api_v1_prefix: str = Field(default="/api/v1")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="KAKUREGA_",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
