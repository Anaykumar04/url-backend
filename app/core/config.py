import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "SwiftLink API"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = "sqlite:///./url_shortener.db"
    BASE_URL: str = "http://urlshortner.1234"
    SECRET_KEY: str = "this_is_a_super_secret_key_change_in_prod"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days

    class Config:
        env_file = ".env"

settings = Settings()
