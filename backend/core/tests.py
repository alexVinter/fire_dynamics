from decimal import Decimal

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from .models import (
    AssemblyTemplate,
    Brand,
    Calculation,
    Component,
    Modification,
    ProtectionZone,
    TechModel,
)


class BrandModelTest(TestCase):
    def test_create_and_str(self):
        b = Brand.objects.create(name="БелАЗ")
        self.assertEqual(str(b), "БелАЗ")
        self.assertEqual(Brand.objects.count(), 1)


class TechModelModelTest(TestCase):
    def test_create_and_str(self):
        brand = Brand.objects.create(name="БелАЗ")
        m = TechModel.objects.create(brand=brand, name="75131")
        self.assertEqual(str(m), "БелАЗ 75131")

    def test_unique_brand_name(self):
        brand = Brand.objects.create(name="БелАЗ")
        TechModel.objects.create(brand=brand, name="75131")
        with self.assertRaises(Exception):
            TechModel.objects.create(brand=brand, name="75131")


class ModificationModelTest(TestCase):
    def test_create_and_str(self):
        brand = Brand.objects.create(name="БелАЗ")
        tech_model = TechModel.objects.create(brand=brand, name="75131")
        mod = Modification.objects.create(model=tech_model, name="75131-10", search_keywords="Самосвал")
        self.assertIn("75131", str(mod))

    def test_unique_model_name(self):
        brand = Brand.objects.create(name="БелАЗ")
        tech_model = TechModel.objects.create(brand=brand, name="75131")
        Modification.objects.create(model=tech_model, name="75131-10")
        with self.assertRaises(Exception):
            Modification.objects.create(model=tech_model, name="75131-10")


class ProtectionZoneModelTest(TestCase):
    def test_create_and_str(self):
        z = ProtectionZone.objects.create(name="Двигатель", code="engine")
        self.assertIn("Двигатель", str(z))

    def test_unique_code(self):
        ProtectionZone.objects.create(name="Зона 1", code="z1")
        with self.assertRaises(Exception):
            ProtectionZone.objects.create(name="Зона 2", code="z1")


class ComponentModelTest(TestCase):
    def test_create_and_str(self):
        c = Component.objects.create(sku="BAL-50", name="Баллон 50л", type="Модуль", price=Decimal("15000.00"))
        self.assertIn("BAL-50", str(c))

    def test_unique_sku(self):
        Component.objects.create(sku="ART-1", name="Товар 1", type="Тип", price=Decimal("100"))
        with self.assertRaises(Exception):
            Component.objects.create(sku="ART-1", name="Другой", type="Тип", price=Decimal("200"))


class AssemblyTemplateModelTest(TestCase):
    def test_create_and_unique_triple(self):
        brand = Brand.objects.create(name="БелАЗ")
        tech_model = TechModel.objects.create(brand=brand, name="75131")
        mod = Modification.objects.create(model=tech_model, name="75131-10")
        zone = ProtectionZone.objects.create(name="Двигатель", code="engine")
        comp = Component.objects.create(sku="BAL-50", name="Баллон", type="Модуль", price=Decimal("10000"))
        t = AssemblyTemplate.objects.create(
            modification=mod, protection_zone=zone, component=comp, quantity=Decimal("2.000")
        )
        self.assertEqual(t.quantity, Decimal("2.000"))
        with self.assertRaises(Exception):
            AssemblyTemplate.objects.create(
                modification=mod, protection_zone=zone, component=comp, quantity=Decimal("3")
            )


class CalculateConfigurationTest(TestCase):
    def test_model_not_found_raises(self):
        from core.services.calculation import calculate_configuration
        with self.assertRaises(ValueError) as ctx:
            calculate_configuration(99999, [1])
        self.assertIn("99999", str(ctx.exception))

    def test_returns_total_price_and_groups(self):
        from core.services.calculation import calculate_configuration
        brand = Brand.objects.create(name="БелАЗ")
        tech_model = TechModel.objects.create(brand=brand, name="75131")
        mod = Modification.objects.create(model=tech_model, name="75131-10")
        zone = ProtectionZone.objects.create(name="Двигатель", code="engine")
        comp = Component.objects.create(sku="BAL-50", name="Баллон", type="Модуль", price=Decimal("10000"))
        AssemblyTemplate.objects.create(
            modification=mod, protection_zone=zone, component=comp, quantity=Decimal("2")
        )
        result = calculate_configuration(mod.id, [zone.id])
        self.assertIn("total_price", result)
        self.assertIn("groups", result)
        self.assertEqual(result["total_price"], 20000)
        self.assertEqual(result["groups"]["Модуль"], [{"id": comp.id, "name": "Баллон", "price": 10000}])


class CalculationModelTest(TestCase):
    def test_create_and_save_zones(self):
        brand = Brand.objects.create(name="БелАЗ")
        tech_model = TechModel.objects.create(brand=brand, name="75131")
        mod = Modification.objects.create(model=tech_model, name="75131-10")
        z1 = ProtectionZone.objects.create(name="Двигатель", code="engine")
        z2 = ProtectionZone.objects.create(name="Гидравлика", code="hydro")
        calc = Calculation.objects.create(model=mod, total_price=Decimal("50000.00"))
        calc.selected_zones.set([z1, z2])
        self.assertEqual(calc.model_id, mod.id)
        self.assertEqual(calc.total_price, Decimal("50000.00"))
        self.assertEqual(set(calc.selected_zones.values_list("id", flat=True)), {z1.id, z2.id})


class ConstructorAPITest(TestCase):
    """Тесты API конструктора (Модуль 3)."""

    def setUp(self):
        self.client = APIClient()
        brand = Brand.objects.create(name="БелАЗ")
        self.tech_model = TechModel.objects.create(brand=brand, name="75131")
        self.mod = Modification.objects.create(
            model=self.tech_model, name="75131-10", search_keywords="Самосвал 787"
        )
        self.zone = ProtectionZone.objects.create(name="Двигатель", code="engine")
        comp = Component.objects.create(sku="BAL-50", name="Баллон", type="Модуль", price=Decimal("10000"))
        AssemblyTemplate.objects.create(
            modification=self.mod, protection_zone=self.zone, component=comp, quantity=Decimal("2")
        )

    def test_models_search_empty(self):
        r = self.client.get("/api/models/", {"search": ""})
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        data = r.json()
        self.assertIsInstance(data, list)
        # Пустой поиск возвращает список всех моделей (для выпадающего списка), в т.ч. нашу
        self.assertIn({"id": self.mod.id, "name": str(self.mod)}, data)

    def test_models_search_by_name(self):
        r = self.client.get("/api/models/", {"search": "75131"})
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        data = r.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["id"], self.mod.id)
        self.assertIn("75131", data[0]["name"])

    def test_models_search_by_keyword(self):
        r = self.client.get("/api/models/", {"search": "Самосвал"})
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(len(r.json()), 1)
        self.assertEqual(r.json()[0]["id"], self.mod.id)

    def test_zones_list(self):
        r = self.client.get("/api/zones/")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        data = r.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["id"], self.zone.id)
        self.assertEqual(data[0]["name"], "Двигатель")

    def test_calculate_ok(self):
        r = self.client.post(
            "/api/calculate/",
            {"model_id": self.mod.id, "zone_ids": [self.zone.id]},
            format="json",
        )
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        data = r.json()
        self.assertIn("total_price", data)
        self.assertIn("groups", data)
        self.assertEqual(data["total_price"], 20000)

    def test_calculate_missing_model_id(self):
        r = self.client.post("/api/calculate/", {"zone_ids": []}, format="json")
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_save_calculation(self):
        r = self.client.post(
            "/api/calculations/save/",
            {
                "model_id": self.mod.id,
                "zone_ids": [self.zone.id],
                "total_price": 20000,
            },
            format="json",
        )
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", r.json())
        calc = Calculation.objects.get(id=r.json()["id"])
        self.assertEqual(calc.model_id, self.mod.id)
        self.assertEqual(int(calc.total_price), 20000)
        self.assertEqual(list(calc.selected_zones.values_list("id", flat=True)), [self.zone.id])


class AIEnrichmentServiceTest(TestCase):
    """Тесты AI-обогащения (Модуль 4)."""

    def test_enrich_existing_incomplete_specs(self):
        from core.services.ai.enrichment import AIEnrichmentService
        brand = Brand.objects.create(name="БелАЗ")
        tech_model = TechModel.objects.create(brand=brand, name="75131")
        mod = Modification.objects.create(model=tech_model, name="75131-10", search_keywords="Самосвал", specs={})
        svc = AIEnrichmentService()
        result = svc.enrich_if_needed("75131-10")
        self.assertEqual(result.id, mod.id)
        mod.refresh_from_db()
        self.assertEqual(mod.specs.get("engine_type"), "V16 Diesel")
        self.assertEqual(mod.specs.get("year"), 2020)

    def test_enrich_existing_complete_specs_no_call(self):
        from core.services.ai.enrichment import AIEnrichmentService
        brand = Brand.objects.create(name="БелАЗ")
        tech_model = TechModel.objects.create(brand=brand, name="75131")
        mod = Modification.objects.create(
            model=tech_model, name="75131-10", specs={"engine_type": "V8", "year": 2019}
        )
        svc = AIEnrichmentService()
        result = svc.enrich_if_needed("75131-10")
        self.assertEqual(result.id, mod.id)
        mod.refresh_from_db()
        self.assertEqual(mod.specs["year"], 2019)

    def test_enrich_creates_when_not_found(self):
        from core.services.ai.enrichment import AIEnrichmentService
        svc = AIEnrichmentService()
        result = svc.enrich_if_needed("Неизвестная машина XYZ")
        self.assertIsNotNone(result.id)
        self.assertEqual(result.specs["engine_type"], "V16 Diesel")
        self.assertEqual(result.specs["year"], 2020)
        self.assertEqual(result.model.brand.name, "Импорт")

    def test_enrich_invalid_specs_raises(self):
        from core.services.ai.enrichment import AIEnrichmentService
        from core.services.ai.mock_client import MockAIClient
        class BadClient(MockAIClient):
            def get_model_specs(self, model_name):
                return {"engine_type": "X", "year": "not-a-number"}
        svc = AIEnrichmentService(client=BadClient())
        with self.assertRaises(ValueError) as ctx:
            svc.enrich_if_needed("Any")
        self.assertIn("year", str(ctx.exception))


class MatcherTest(TestCase):
    """Тесты find_best_match (Модуль 5): точное совпадение, синоним, опечатка."""

    def setUp(self):
        brand = Brand.objects.create(name="БелАЗ")
        self.tech_model = TechModel.objects.create(brand=brand, name="75131")
        self.mod = Modification.objects.create(
            model=self.tech_model,
            name="75131-10",
            search_keywords="Самосвал 787, HD 787",
        )

    def test_exact_match_by_name(self):
        from core.services.matcher import find_best_match
        result = find_best_match("БелАЗ 75131 75131-10")
        self.assertEqual(result, self.mod.id)

    def test_synonym_match_by_keywords(self):
        from core.services.matcher import find_best_match
        result = find_best_match("Самосвал 787")
        # Может вернуться id (score > 85) или список вариантов (50 <= score <= 85)
        if isinstance(result, int):
            self.assertEqual(result, self.mod.id)
        else:
            self.assertIsInstance(result, list)
            self.assertGreater(len(result), 0)
            self.assertEqual(result[0]["id"], self.mod.id)

    def test_typo_returns_fuzzy_list_or_id(self):
        from core.services.matcher import find_best_match
        # Опечатка: латинская s вместо кириллической З — матчер возвращает список (fuzzy) или id
        result = find_best_match("БелАs 75131")
        if isinstance(result, int):
            self.assertEqual(result, self.mod.id)
        else:
            self.assertIsInstance(result, list)
            self.assertGreater(len(result), 0)
            self.assertLessEqual(len(result), 3)
            self.assertEqual(result[0]["id"], self.mod.id)
            self.assertIn("score", result[0])


class BulkConfirmTest(TestCase):
    """Массовое создание расчётов в транзакции: при ошибке откат."""

    def setUp(self):
        self.client = APIClient()
        brand = Brand.objects.create(name="БелАЗ")
        tech_model = TechModel.objects.create(brand=brand, name="75131")
        self.mod = Modification.objects.create(model=tech_model, name="75131-10")
        self.zone = ProtectionZone.objects.create(name="Двигатель", code="engine")

    def test_bulk_rollback_on_error(self):
        """При невалидной строке (несуществующий id) ни один расчёт не создаётся."""
        before = Calculation.objects.count()
        r = self.client.post(
            "/api/calculations/bulk/",
            {
                "rows": [
                    {"matched_id": self.mod.id, "zone_id": self.zone.id},
                    {"matched_id": 99999, "zone_id": self.zone.id},
                ],
            },
            format="json",
        )
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Calculation.objects.count(), before)
