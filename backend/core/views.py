"""
API для конструктора (Модуль 3).
"""

from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import Calculation, Modification, ProtectionZone
from core.services.calculation import calculate_configuration


class ModelsSearchView(APIView):
    """GET /api/models/?search= — поиск модификаций по названию и синонимам."""

    def get(self, request):
        search = (request.query_params.get("search") or "").strip()
        if not search:
            return Response([])
        qs = (
            Modification.objects.filter(
                Q(name__icontains=search) | Q(search_keywords__icontains=search)
            )
            .select_related("model", "model__brand")[:50]
        )
        return Response([{"id": m.id, "name": str(m)} for m in qs])


class ZonesListView(APIView):
    """GET /api/zones/ — список всех зон защиты."""

    def get(self, request):
        zones = ProtectionZone.objects.all().order_by("name")
        return Response([{"id": z.id, "name": z.name} for z in zones])


@method_decorator(csrf_exempt, name="dispatch")
class CalculateView(APIView):
    """POST /api/calculate/ — расчёт комплектации (вызов Calculation Core)."""

    def post(self, request):
        model_id = request.data.get("model_id")
        zone_ids = request.data.get("zone_ids") or []
        if model_id is None:
            return Response(
                {"error": "model_id обязателен"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            result = calculate_configuration(int(model_id), list(zone_ids))
            return Response(result)
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


@method_decorator(csrf_exempt, name="dispatch")
class SaveCalculationView(APIView):
    """POST /api/calculations/save/ — сохранить расчёт в модель Calculation."""

    def post(self, request):
        model_id = request.data.get("model_id")
        zone_ids = request.data.get("zone_ids") or []
        total_price = request.data.get("total_price")
        if model_id is None or total_price is None:
            return Response(
                {"error": "model_id и total_price обязательны"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        modification = Modification.objects.filter(id=int(model_id)).first()
        if not modification:
            return Response(
                {"error": "Модификация не найдена"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        calc = Calculation.objects.create(
            model=modification,
            total_price=total_price,
        )
        if zone_ids:
            calc.selected_zones.set(ProtectionZone.objects.filter(id__in=zone_ids))
        return Response({"id": calc.id}, status=status.HTTP_201_CREATED)
