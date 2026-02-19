# Release notes: Модуль 1 — Инициализация и БД справочников

## Что сделано

1. **Инфраструктура**
   - Проект поднят в Docker: сервисы `db` (PostgreSQL 15), `backend` (Django), `frontend` (React + Vite).
   - Backend на порту 8000, frontend на 5173. Подключение к БД через переменные окружения.

2. **Модели БД (приложение `core`)**
   - **Brand** — бренд техники.
   - **TechModel** — модель (связь с брендом), UNIQUE (brand, name).
   - **Modification** — модификация (связь с моделью), поле синонимов `search_keywords`, UNIQUE (model, name).
   - **ProtectionZone** — зона защиты (name, code с UNIQUE).
   - **Component** — компонент/запчасть (sku UNIQUE, name, type, price).
   - **AssemblyTemplate** — матрица комплектации: связь (modification, protection_zone, component) + quantity; UNIQUE по тройке полей. Все FK с `on_delete=CASCADE`.

3. **Django Admin**
   - Все модели зарегистрированы. Поиск (`search_fields`), списки (`list_display`) и фильтры (`list_filter`) настроены для удобного ручного наполнения справочников менеджером.
   - В выпадающих списках отображаются названия (методы `__str__` у моделей).

4. **Качество**
   - Backend: линтер **Ruff** (конфиг в `backend/pyproject.toml`).
   - Frontend: линтер **ESLint** (конфиг в `frontend/.eslintrc.cjs`).
   - Базовые unit-тесты приложения `core`: создание записей, проверка уникальности (Brand, TechModel, Modification, ProtectionZone, Component, AssemblyTemplate).

---

# Release notes: Модуль 2 — Логика «Конструктора» (Calculation Core)

## Что сделано

- Сервис расчёта комплектации: `core/services/calculation.py`, функция `calculate_configuration(model_id, zone_ids)`.
- Принимает ID модификации и список ID зон; возвращает `total_price` и `groups` (компоненты по типам). Базовый шаблон — зона с `code='BASE'`.
- Unit-тесты расчёта в `core/tests.py` (CalculateConfigurationTest).

## Как проверить

- **Тесты:** `docker compose exec backend python manage.py test core` — все тесты зелёные.
- **Линтер:** `docker compose exec backend ruff check .` — без ошибок.

**Ручная проверка расчёта (Django shell):**

```bash
docker compose exec backend python manage.py shell
```

В shell по очереди:

```python
from core.services.calculation import calculate_configuration
calculate_configuration(1, [2])
```

Подставь свои `modification_id` и `zone_id` из админки. Ожидается словарь с `total_price` и `groups`.

---

# Release notes: Модуль 3 — UI одиночного расчёта (MVP Interface)

## Что сделано

**Backend**

- Подключены Django REST Framework и django-cors-headers.
- Модель **Calculation**: модификация (FK), выбранные зоны (M2M), итоговая цена, дата создания. Регистрация в админке.
- API: `GET /api/models/?search=`, `GET /api/zones/`, `POST /api/calculate/`, `POST /api/calculations/save/`.
- Миграция `0002_add_calculation`. Unit-тесты: CalculationModelTest, ConstructorAPITest.

**Frontend**

- Страница **ConstructorPage**: поиск техники (live-search 300 ms), чекбоксы зон, итоговая спецификация и цена, кнопка «Сохранить расчёт».
- API-клиент в `src/api.js`, базовый URL из `VITE_API_URL`.

## Как проверить

- **Миграции:** `docker compose exec backend python manage.py migrate`
- **В браузере:** http://localhost:5173 — поиск, выбор модели и зон, сохранение расчёта. В админке — раздел «Расчёты».

---

## Как проверить (общее)

### Запуск проекта

```bash
docker compose up --build -d
```

Создание суперпользователя (один раз):

```bash
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py createsuperuser
```

### Сборка (Build)

- **Backend:** образ собирается при `docker compose up --build`. Дополнительно: `docker compose build backend`.
- **Frontend:** `docker compose exec frontend npm run build` — сборка должна завершиться без ошибок.

### Статический анализ (Linter)

- **Backend:**  
  `docker compose exec backend ruff check .`  
  Ожидается: вывод без ошибок (или только предупреждения по соглашению проекта).

- **Frontend:**  
  `docker compose exec frontend npm run lint`  
  Ожидается: вывод без ошибок.

### Unit-тесты

```bash
docker compose exec backend python manage.py test core
```

Ожидается: все тесты пройдены (OK).

---
