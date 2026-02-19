from django.db import models


class Brand(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название')

    class Meta:
        db_table = 'core_brand'
        verbose_name = 'Бренд'
        verbose_name_plural = 'Бренды'

    def __str__(self):
        return self.name


class TechModel(models.Model):
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, verbose_name='Бренд')
    name = models.CharField(max_length=255, verbose_name='Название')

    class Meta:
        db_table = 'core_model'
        verbose_name = 'Модель техники'
        verbose_name_plural = 'Модели техники'
        constraints = [
            models.UniqueConstraint(fields=['brand', 'name'], name='core_techmodel_brand_name_uniq'),
        ]

    def __str__(self):
        return f'{self.brand.name} {self.name}'


class Modification(models.Model):
    model = models.ForeignKey(TechModel, on_delete=models.CASCADE, verbose_name='Модель техники')
    name = models.CharField(max_length=255, verbose_name='Название')
    search_keywords = models.TextField(blank=True, verbose_name='Синонимы для поиска')

    class Meta:
        db_table = 'core_modification'
        verbose_name = 'Модификация'
        verbose_name_plural = 'Модификации'
        constraints = [
            models.UniqueConstraint(fields=['model', 'name'], name='core_modification_model_name_uniq'),
        ]

    def __str__(self):
        return f'{self.model} {self.name}' if self.name else str(self.model)


class ProtectionZone(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название')
    code = models.CharField(max_length=50, unique=True, verbose_name='Код')

    class Meta:
        db_table = 'core_protectionzone'
        verbose_name = 'Зона защиты'
        verbose_name_plural = 'Зоны защиты'

    def __str__(self):
        return f'{self.name} ({self.code})'


class Component(models.Model):
    sku = models.CharField(max_length=100, unique=True, verbose_name='Артикул')
    name = models.CharField(max_length=255, verbose_name='Название')
    type = models.CharField(max_length=100, verbose_name='Тип')
    price = models.DecimalField(max_digits=14, decimal_places=2, verbose_name='Цена')

    class Meta:
        db_table = 'core_component'
        verbose_name = 'Компонент'
        verbose_name_plural = 'Компоненты'

    def __str__(self):
        return f'{self.sku} — {self.name}'


class AssemblyTemplate(models.Model):
    modification = models.ForeignKey(Modification, on_delete=models.CASCADE, verbose_name='Модификация')
    protection_zone = models.ForeignKey(ProtectionZone, on_delete=models.CASCADE, verbose_name='Зона защиты')
    component = models.ForeignKey(Component, on_delete=models.CASCADE, verbose_name='Компонент')
    quantity = models.DecimalField(max_digits=12, decimal_places=3, verbose_name='Количество')

    class Meta:
        db_table = 'core_assemblytemplate'
        verbose_name = 'Шаблон комплектации'
        verbose_name_plural = 'Шаблоны комплектации'
        constraints = [
            models.UniqueConstraint(
                fields=['modification', 'protection_zone', 'component'],
                name='core_assemblytemplate_mod_zone_comp_uniq',
            ),
        ]

    def __str__(self):
        return f'{self.modification} / {self.protection_zone} / {self.component}: {self.quantity}'


class Calculation(models.Model):
    """Сохранённый расчёт (Модуль 3)."""

    model = models.ForeignKey(
        Modification,
        on_delete=models.CASCADE,
        verbose_name='Модификация',
        related_name='calculations',
    )
    selected_zones = models.ManyToManyField(
        ProtectionZone,
        blank=True,
        verbose_name='Выбранные зоны',
        related_name='calculations',
    )
    total_price = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        verbose_name='Итоговая цена',
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        db_table = 'core_calculation'
        verbose_name = 'Расчёт'
        verbose_name_plural = 'Расчёты'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.model} — {self.total_price} ({self.created_at})'
