from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "ITCC Wisuda Synchronization API"
    app_env: str = "development"
    frontend_url: str = "http://localhost:3000"
    supabase_url: str
    supabase_service_role_key: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
