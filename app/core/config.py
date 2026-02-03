from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://user:password@localhost:5432/crypto_analytics"
    api_title: str = "Crypto Analytics API"
    api_version: str = "1.0.0"
    coingecko_api_url: str = "https://api.coingecko.com/api/v3"
    coingecko_api_key: str = ""
    coingecko_timeout: float = 10.0
    ingest_interval_minutes: int = 5
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    return Settings()
