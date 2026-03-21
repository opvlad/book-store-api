from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    database_url: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/bookstore"
    )
    secret_key: str = "dev-secret-key-change-this-later"
    access_token_expire_minutes: int = 30
    algorithm: str = "HS256"


settings = Settings()
