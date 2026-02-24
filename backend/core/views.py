"""
API для конструктора (Модуль 3) и пакетной загрузки (Модуль 5).
"""

from django.db import transaction
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import Calculation, Modification, ProtectionZone
from core.services.ai.enrichment import AIEnrichmentService
from core.services.calculation import calculate_configuration


class ModelsSearchView(APIView):
    """GET /api/models/?search= — поиск модификаций по названию и синонимам."""

    def get(self, request):
        search = (request.query_params.get("search") or "").strip()
        if search:
            qs = (
                Modification.objects.filter(
                    Q(name__icontains=search) | Q(search_keywords__icontains=search)
                )
                .select_related("model", "model__brand")[:50]
            )
        else:
            qs = (
                Modification.objects.all()
                .select_related("model", "model__brand")
                .order_by("model__brand__name", "model__name", "name")[:300]
            )
        return Response([{"id": m.id, "name": str(m)} for m in qs])


class ZonesListView(APIView):
    """GET /api/zones/ — список всех зон защиты."""

    def get(self, request):
        zones = ProtectionZone.objects.all().order_by("name")
        return Response([{"id": z.id, "name": z.name} for z in zones])


@method_decorator(csrf_exempt, name="dispatch")
class CalculateView(APIView):
    """POST /api/calculate/ — расчёт комплектации (Calculation Core + AI-обогащение при необходимости)."""

    def post(self, request):
        model_id = request.data.get("model_id")
        zone_ids = request.data.get("zone_ids") or []
        if model_id is None:
            return Response(
                {"error": "model_id обязателен"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        modification = Modification.objects.filter(id=int(model_id)).select_related("model", "model__brand").first()
        if not modification:
            return Response(
                {"error": "Модификация не найдена"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            enrichment = AIEnrichmentService()
            modification = enrichment.enrich_modification(modification)
            result = calculate_configuration(modification.id, list(zone_ids))
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


@method_decorator(csrf_exempt, name="dispatch")
class BulkUploadView(APIView):
    """POST /api/bulk-upload/ — загрузка .xlsx, нечёткий поиск по колонке «Техника»."""

    def post(self, request):
        try:
            import pandas as pd
            from core.services.matcher import find_best_match
        except ImportError as e:
            return Response(
                {
                    "error": (
                        "В образе backend не установлены pandas или rapidfuzz. "
                        "Пересоберите образ: docker compose build backend --no-cache && docker compose up -d backend"
                    ),
                    "detail": str(e),
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        file_obj = request.FILES.get("file")
        if not file_obj:
            return Response(
                {"error": "Файл не передан. Используйте поле 'file'."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not file_obj.name.endswith(".xlsx"):
            return Response(
                {"error": "Ожидается файл .xlsx"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            df = pd.read_excel(file_obj, engine="openpyxl")
        except Exception as e:
            return Response(
                {"error": f"Ошибка чтения Excel: {e!s}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        required = ["Техника", "Зона защиты"]
        missing = [c for c in required if c not in df.columns]
        if missing:
            return Response(
                {"error": f"В файле должны быть колонки: {required}. Не найдены: {missing}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        rows_out = []
        for _, row in df.iterrows():
            original_text = (
                str(row["Техника"]).strip()
                if pd.notna(row.get("Техника")) and str(row["Техника"]).strip()
                else ""
            )
            original_zone = (
                str(row["Зона защиты"]).strip()
                if pd.notna(row.get("Зона защиты"))
                else ""
            )
            if not original_text:
                rows_out.append({
                    "original_text": "",
                    "original_zone": original_zone,
                    "matched_id": None,
                    "confidence": 0,
                    "status": "not_found",
                })
                continue
            match = find_best_match(original_text)
            if isinstance(match, int):
                rows_out.append({
                    "original_text": original_text,
                    "original_zone": original_zone,
                    "matched_id": match,
                    "confidence": 100,
                    "status": "exact",
                })
            elif isinstance(match, list) and match:
                first = match[0]
                rows_out.append({
                    "original_text": original_text,
                    "original_zone": original_zone,
                    "matched_id": first["id"],
                    "confidence": first["score"],
                    "status": "fuzzy",
                })
            else:
                rows_out.append({
                    "original_text": original_text,
                    "original_zone": original_zone,
                    "matched_id": None,
                    "confidence": 0,
                    "status": "not_found",
                })
        return Response({"rows": rows_out})


@method_decorator(csrf_exempt, name="dispatch")
class BulkConfirmView(APIView):
    """POST /api/calculations/bulk/ — массовое создание расчётов в одной транзакции."""

    def post(self, request):
        rows = request.data.get("rows") or []
        if not rows:
            return Response(
                {"error": "Передайте массив rows: [{ matched_id, zone_id }, ...]"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            with transaction.atomic():
                created = []
                for i, row in enumerate(rows):
                    matched_id = row.get("matched_id")
                    zone_id = row.get("zone_id")
                    if matched_id is None or zone_id is None:
                        raise ValueError(
                            f"Строка {i + 1}: обязательны matched_id и zone_id"
                        )
                    modification = Modification.objects.filter(id=int(matched_id)).first()
                    if not modification:
                        raise ValueError(f"Строка {i + 1}: модификация id={matched_id} не найдена")
                    zone = ProtectionZone.objects.filter(id=int(zone_id)).first()
                    if not zone:
                        raise ValueError(f"Строка {i + 1}: зона id={zone_id} не найдена")
                    result = calculate_configuration(modification.id, [zone.id])
                    calc = Calculation.objects.create(
                        model=modification,
                        total_price=result["total_price"],
                    )
                    calc.selected_zones.add(zone)
                    created.append({"id": calc.id})
            return Response({"created": created, "count": len(created)}, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
