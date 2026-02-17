from decimal import Decimal

from django.test import TestCase

from .models import (
    AssemblyTemplate,
    Brand,
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
