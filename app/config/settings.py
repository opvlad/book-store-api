from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    database_url: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/bookstore"
    )
    redis_url: str = "redis://localhost:6379"
    secret_key: str = "dev-secret-key-change-this-later"
    access_token_expire_minutes: int = 30
    algorithm: str = "HS256"
    resend_api_key: str = "resend-api-key"
    email_sender: str = "email@example.com"


settings = Settings()


priority_points = {
    "user_status": {
        "regular": 2,
        "loyal": 5,
        "vip": 10,
    },
    "delivery_type": {
        "standard": 2,
        "express": 5,
        "urgent": 10,
    },
    "order_amount": {
        "under_500": 2,
        "in_range_500_2000": 6,
        "over_2000": 10,
    },
}
