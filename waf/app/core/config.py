from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    DATABASE_URL: str = "postgresql+asyncpg://waf_user:waf_password@postgres:5432/waf_db"
    REDIS_URL: str = "redis://redis:6379/0"
    BACKEND_URL: str = "http://backend:8001"
    WAF_HOST: str = "0.0.0.0"
    WAF_PORT: int = 8000
    THREAT_SCORE_THRESHOLD: int = 50

    POSTGRES_USER: str = "waf_user"
    POSTGRES_PASSWORD: str = "waf_password"
    POSTGRES_DB: str = "waf_db"


settings = Settings()
