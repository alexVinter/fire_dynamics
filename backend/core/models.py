from django.db import models


class Brand(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        db_table = 'core_brand'

    def __str__(self):
        return self.name


class TechModel(models.Model):
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    class Meta:
        db_table = 'core_model'
        constraints = [
            models.UniqueConstraint(fields=['brand', 'name'], name='core_techmodel_brand_name_uniq'),
        ]

    def __str__(self):
        return f'{self.brand.name} {self.name}'


class Modification(models.Model):
    model = models.ForeignKey(TechModel, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    search_keywords = models.TextField(blank=True)

    class Meta:
        db_table = 'core_modification'
        constraints = [
            models.UniqueConstraint(fields=['model', 'name'], name='core_modification_model_name_uniq'),
        ]

    def __str__(self):
        return f'{self.model} {self.name}' if self.name else str(self.model)


class ProtectionZone(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, unique=True)

    class Meta:
        db_table = 'core_protectionzone'

    def __str__(self):
        return f'{self.name} ({self.code})'


class Component(models.Model):
    sku = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=14, decimal_places=2)

    class Meta:
        db_table = 'core_component'

    def __str__(self):
        return f'{self.sku} — {self.name}'


class AssemblyTemplate(models.Model):
    modification = models.ForeignKey(Modification, on_delete=models.CASCADE)
    protection_zone = models.ForeignKey(ProtectionZone, on_delete=models.CASCADE)
    component = models.ForeignKey(Component, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=12, decimal_places=3)

    class Meta:
        db_table = 'core_assemblytemplate'
        constraints = [
            models.UniqueConstraint(
                fields=['modification', 'protection_zone', 'component'],
                name='core_assemblytemplate_mod_zone_comp_uniq',
            ),
        ]

    def __str__(self):
        return f'{self.modification} / {self.protection_zone} / {self.component}: {self.quantity}'
