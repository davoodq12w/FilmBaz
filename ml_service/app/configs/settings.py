from pydantic_settings import BaseSettings

DATABASE_URL = "postgresql+asyncpg://ml_service:MlServicePassword@db:5432/filmbaz_db"


class Settings(BaseSettings):
    DATABASE_URL: str = DATABASE_URL


settings = Settings()
