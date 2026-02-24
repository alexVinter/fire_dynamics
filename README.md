# Динамика огня

Каталог техники и конструктор комплектации систем (тушение). Стек: Django, React + Vite, PostgreSQL, Docker. Модули 1–3: справочники, расчёт комплектации, UI конструктора.

## Запуск проекта

1. Установить Docker Desktop
2. В корне проекта выполнить:

```bash
docker compose up --build
```

**Если пакетная загрузка .xlsx не работает** (ошибка про pandas/rapidfuzz), пакеты должны быть в образе backend. Пересоберите образ (при медленном интернете может понадобиться несколько попыток):

```bash
docker compose build backend --no-cache
docker compose up -d backend
```

Проверка: `docker compose exec backend pip list | findstr "pandas rapidfuzz"` — должны быть в списке.

3. Для создания суперпользователя:

```bash
docker compose exec backend python manage.py createsuperuser
```

---

## Проверка (Build, Linter, тесты)

- **Сборка frontend:** `docker compose exec frontend npm run build`
- **Линтер backend:** `docker compose exec backend ruff check .`
- **Линтер frontend:** `docker compose exec frontend npm run lint`
- **Тесты:** `docker compose exec backend python manage.py test core`

Подробнее: [RELEASE_NOTES.md](RELEASE_NOTES.md).
