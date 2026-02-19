"""
Сервис расчёта комплектации (Модуль 2: Calculation Core).

Базовый шаблон определяется по зоне с code='BASE'.
Модели не изменяются.
"""

from collections import defaultdict
from decimal import Decimal

from django.db.models import Q

from core.models import AssemblyTemplate, Component, Modification, ProtectionZone


def calculate_configuration(model_id: int, zone_ids: list[int]) -> dict:
    """
    Рассчитать комплектацию для модификации техники и выбранных зон.

    Args:
        model_id: ID модификации (Modification.id).
        zone_ids: Список ID зон защиты.

    Returns:
        {
            "total_price": int,
            "groups": {
                "тип_компонента": [{"id": int, "name": str, "price": int}, ...]
            }
        }

    Raises:
        ValueError: Если модификация не найдена.
    """
    modification = Modification.objects.filter(id=model_id).first()
    if not modification:
        raise ValueError(f"Модификация с id={model_id} не найдена.")

    base_zone = ProtectionZone.objects.filter(code="BASE").first()
    base_zone_id = base_zone.id if base_zone else None

    templates_qs = AssemblyTemplate.objects.filter(
        modification_id=model_id
    ).select_related("component")

    base_condition = Q(protection_zone_id=base_zone_id) if base_zone_id else Q(pk__in=[])
    zone_condition = Q(protection_zone_id__in=zone_ids) if zone_ids else Q(pk__in=[])

    templates = list(
        templates_qs.filter(base_condition | zone_condition)
    )

    component_quantities: dict[int, Decimal] = {}
    component_by_id: dict[int, Component] = {}

    for t in templates:
        cid = t.component_id
        component_quantities[cid] = component_quantities.get(cid, Decimal("0")) + t.quantity
        component_by_id[cid] = t.component

    total_price = Decimal("0")
    for cid, c in component_by_id.items():
        total_price += c.price * component_quantities[cid]

    groups: dict[str, list[dict]] = defaultdict(list)
    for c in component_by_id.values():
        type_name = c.type or "Прочее"
        groups[type_name].append({
            "id": c.id,
            "name": c.name,
            "price": int(c.price),
        })

    return {
        "total_price": int(total_price),
        "groups": dict(groups),
    }
