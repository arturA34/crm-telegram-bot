from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Telegram
    bot_token: str

    # PostgreSQL
    postgres_host: str = "postgres"
    postgres_port: int = 5432
    postgres_user: str = "crm_bot"
    postgres_password: str = "crm_bot_secret"
    postgres_db: str = "crm_bot"

    # Redis
    redis_host: str = "redis"
    redis_port: int = 6379
    redis_db: int = 0

    # Application
    log_level: str = "INFO"
    debug: bool = False

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def redis_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"


def get_settings() -> Settings:
    return Settings()
