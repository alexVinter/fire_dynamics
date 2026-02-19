# Динамика огня

Каталог техники и конструктор комплектации систем (тушение). Стек: Django, React + Vite, PostgreSQL, Docker. Модули 1–3: справочники, расчёт комплектации, UI конструктора.

## Запуск проекта

1. Установить Docker Desktop
2. В корне проекта выполнить:

```bash
docker compose up --build
```

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
