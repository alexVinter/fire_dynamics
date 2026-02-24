"""
Интерфейс AI-клиента для обогащения данных (Модуль 4).
"""


class BaseAIClient:
    """Базовый класс клиента: получение характеристик модели техники от AI."""

    def get_model_specs(self, model_name: str) -> dict:
        """
        Запросить у AI характеристики модели (engine_type, year).

        Returns:
            {"engine_type": str, "year": int}

        Raises:
            NotImplementedError: должен быть реализован в подклассе.
        """
        raise NotImplementedError
