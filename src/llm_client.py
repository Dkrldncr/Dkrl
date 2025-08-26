from typing import List, Dict
from openai import OpenAI
from .config import load_config


class LLMClient:
    def __init__(self) -> None:
        config = load_config()
        if not config.openai_api_key:
            raise ValueError("OPENAI_API_KEY bulunamadı. Lütfen .env dosyasını doldurun.")
        self._client = OpenAI(api_key=config.openai_api_key)
        self._model = config.openai_model

    def chat(self, messages: List[Dict[str, str]]) -> str:
        response = self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            temperature=0.2,
        )
        return response.choices[0].message.content or ""