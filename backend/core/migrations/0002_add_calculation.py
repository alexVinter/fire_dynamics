# Generated manually for Модуль 3

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Calculation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_price', models.DecimalField(decimal_places=2, default=0, max_digits=14, verbose_name='Итоговая цена')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('model', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='calculations', to='core.modification', verbose_name='Модификация')),
                ('selected_zones', models.ManyToManyField(blank=True, related_name='calculations', to='core.protectionzone', verbose_name='Выбранные зоны')),
            ],
            options={
                'verbose_name': 'Расчёт',
                'verbose_name_plural': 'Расчёты',
                'db_table': 'core_calculation',
                'ordering': ['-created_at'],
            },
        ),
    ]
