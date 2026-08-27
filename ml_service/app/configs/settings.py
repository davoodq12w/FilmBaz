from pydantic_settings import BaseSettings
from decouple import config


class Settings(BaseSettings):
    DATABASE_URL: str = config("DATABASE_URL")


settings = Settings()
