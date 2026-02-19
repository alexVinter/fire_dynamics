from django.contrib import admin

from .models import (
    AssemblyTemplate,
    Brand,
    Calculation,
    Component,
    Modification,
    ProtectionZone,
    TechModel,
)


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(TechModel)
class TechModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'brand')
    list_filter = ('brand',)
    search_fields = ('name', 'brand__name')


@admin.register(Modification)
class ModificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'model', 'search_keywords')
    list_filter = ('model__brand', 'model')
    search_fields = ('name', 'search_keywords', 'model__name', 'model__brand__name')


@admin.register(ProtectionZone)
class ProtectionZoneAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'code')
    search_fields = ('name', 'code')


@admin.register(Component)
class ComponentAdmin(admin.ModelAdmin):
    list_display = ('sku', 'name', 'type', 'price')
    list_display_links = ('sku',)
    list_filter = ('type',)
    search_fields = ('sku', 'name')


@admin.register(AssemblyTemplate)
class AssemblyTemplateAdmin(admin.ModelAdmin):
    list_display = ('modification', 'protection_zone', 'component', 'quantity')
    list_filter = ('modification', 'protection_zone')


@admin.register(Calculation)
class CalculationAdmin(admin.ModelAdmin):
    list_display = ('id', 'model', 'total_price', 'created_at')
    list_filter = ('created_at',)
    readonly_fields = ('created_at',)
    filter_horizontal = ('selected_zones',)
