#!/usr/bin/env python
"""Скрипт проверки моделей core — запуск: docker compose exec backend python check_models.py"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Brand, TechModel, Modification, ProtectionZone, Component, AssemblyTemplate

print('Записей в таблицах:')
print('  Brand:', Brand.objects.count())
print('  TechModel:', TechModel.objects.count())
print('  Modification:', Modification.objects.count())
print('  ProtectionZone:', ProtectionZone.objects.count())
print('  Component:', Component.objects.count())
print('  AssemblyTemplate:', AssemblyTemplate.objects.count())
