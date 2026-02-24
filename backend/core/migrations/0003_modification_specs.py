# Модуль 4: поле Specs для AI-обогащения

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0002_add_calculation"),
    ]

    operations = [
        migrations.AddField(
            model_name="modification",
            name="specs",
            field=models.JSONField(blank=True, default=dict, verbose_name="Характеристики (AI)"),
        ),
    ]
