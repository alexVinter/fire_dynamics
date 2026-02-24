"""
Заглушка AI-клиента (Модуль 4). Используется до подключения реального API.

# TODO: Replace MockAIClient with OpenAIClient when API key is available
"""

from .client import BaseAIClient


class MockAIClient(BaseAIClient):
    """Возвращает фиксированные Specs без вызова внешнего API."""

    def get_model_specs(self, model_name: str) -> dict:
        return {
            "engine_type": "V16 Diesel",
            "year": 2020,
        }
