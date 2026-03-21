from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Automat Washing"
    secret_key: str = "change-me-in-production-use-openssl-rand-hex-32"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 12
    database_url: str = "sqlite:///./autowash.db"
    cors_origins: str = (
        "http://localhost:5173,http://127.0.0.1:5173,"
        "http://localhost:5174,http://127.0.0.1:5174,"
        "http://localhost:5175,http://127.0.0.1:5175,"
        "http://localhost:8080,http://127.0.0.1:8080"
    )
    # Optional regex (e.g. https://.*\\.vercel\\.app) so preview deployments work without listing every URL.
    cors_origin_regex: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
