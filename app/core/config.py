import os
from typing import List


class Settings:
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-please")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    CORS_ORIGINS: List[str] = os.getenv("CORS_ORIGINS", "*").split(",")


settings = Settings()