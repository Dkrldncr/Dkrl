import os
from dataclasses import dataclass
from dotenv import load_dotenv


load_dotenv()


@dataclass
class AppConfig:
    openai_api_key: str
    openai_model: str


def load_config() -> AppConfig:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()
    return AppConfig(openai_api_key=api_key, openai_model=model)