"""
Сервис обогащения данных модели техники через AI (Модуль 4).

Не вызывать AI из view напрямую — только через этот сервис.
"""

from core.models import Brand, Modification, TechModel

# TODO: Replace MockAIClient with OpenAIClient when API key is available
from .mock_client import MockAIClient


def _validate_specs(data: dict) -> None:
    """Проверить формат ответа AI. При ошибке — ValueError."""
    if not isinstance(data, dict):
        raise ValueError("Ответ AI должен быть словарём")
    if "engine_type" not in data or not isinstance(data["engine_type"], str):
        raise ValueError("В ответе AI должен быть engine_type (строка)")
    if "year" not in data:
        raise ValueError("В ответе AI должен быть year")
    try:
        year = int(data["year"])
    except (TypeError, ValueError):
        raise ValueError("year должен быть целым числом")
    if year < 1900 or year > 2100:
        raise ValueError("year вне допустимого диапазона")


def _specs_complete(specs: dict) -> bool:
    """Проверить, что в Specs есть engine_type и year (int)."""
    if not specs:
        return False
    if not isinstance(specs.get("engine_type"), str) or not specs.get("engine_type").strip():
        return False
    try:
        y = specs.get("year")
        int(y)
        return 1900 <= int(y) <= 2100
    except (TypeError, ValueError):
        return False


class AIEnrichmentService:
    """
    Обогащение модификации техники: при необходимости запрос к AI и сохранение Specs.
    """

    def __init__(self, client=None):
        self.client = client if client is not None else MockAIClient()

    def enrich_modification(self, modification: Modification) -> Modification:
        """
        Обогатить переданную модификацию, если Specs неполные.
        Не ищет и не создаёт другие записи — только обновляет specs у этой.
        """
        if _specs_complete(modification.specs or {}):
            return modification
        raw = self.client.get_model_specs(str(modification))
        _validate_specs(raw)
        modification.specs = {"engine_type": raw["engine_type"], "year": int(raw["year"])}
        modification.save(update_fields=["specs"])
        return modification

    def enrich_if_needed(self, model_name: str):
        """
        Найти или создать модификацию по имени и при необходимости обогатить Specs через AI.

        - Если модификация найдена и Specs полные — вернуть её без вызова AI.
        - Если найдена, но Specs неполные — запросить AI, валидировать, обновить и сохранить.
        - Если не найдена — запросить AI, создать Brand/TechModel/Modification с Specs.

        Args:
            model_name: Строка поиска (название или синоним модели).

        Returns:
            Modification: найденная или созданная модификация с заполненными Specs.

        Raises:
            ValueError: если ответ AI невалидный (данные не сохраняются).
        """
        model_name = (model_name or "").strip()
        if not model_name:
            raise ValueError("model_name не может быть пустым")

        modification = self._find_modification(model_name)

        if modification:
            if _specs_complete(modification.specs or {}):
                return modification
            raw = self.client.get_model_specs(model_name)
            _validate_specs(raw)
            modification.specs = {"engine_type": raw["engine_type"], "year": int(raw["year"])}
            modification.save(update_fields=["specs"])
            return modification

        raw = self.client.get_model_specs(model_name)
        _validate_specs(raw)
        specs = {"engine_type": raw["engine_type"], "year": int(raw["year"])}

        brand, _ = Brand.objects.get_or_create(name="Импорт", defaults={"name": "Импорт"})
        short_name = model_name[:255] if len(model_name) <= 255 else model_name[:252] + "..."
        tech_model, _ = TechModel.objects.get_or_create(
            brand=brand, name=short_name, defaults={"brand": brand, "name": short_name}
        )
        modification = Modification.objects.create(
            model=tech_model,
            name="Базовая",
            search_keywords=model_name,
            specs=specs,
        )
        return modification

    def _find_modification(self, model_name: str):
        """Найти модификацию по имени или синонимам (первое совпадение)."""
        from django.db.models import Q

        qs = (
            Modification.objects.filter(
                Q(name__icontains=model_name) | Q(search_keywords__icontains=model_name)
            )
            .select_related("model", "model__brand")
            .first()
        )
        return qs
