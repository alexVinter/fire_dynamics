# Запуск проекта

1. Установить Docker Desktop
2. В корне проекта выполнить:

```bash
docker compose up --build
```

3. Для создания суперпользователя:

```bash
docker compose exec backend python manage.py createsuperuser
```
