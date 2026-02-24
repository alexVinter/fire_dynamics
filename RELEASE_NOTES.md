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

# Release notes: Модуль 4 — AI-агент для обогащения данных

## Что сделано

- **Модель:** у `Modification` добавлено поле `specs` (JSONField): `engine_type`, `year` для будущего точного подбора.
- **Сервисы в `core/services/ai/`:**
  - `client.py` — абстрактный `BaseAIClient.get_model_specs(model_name) -> dict`.
  - `mock_client.py` — `MockAIClient` (заглушка, возвращает фиксированные данные).
  - `enrichment.py` — `AIEnrichmentService.enrich_if_needed(model_name)`: поиск модификации, при неполных Specs — вызов AI, валидация, создание/обновление.
- **Интеграция:** перед расчётом (`POST /api/calculate/`) вызывается обогащение выбранной модификации; при невалидном ответе AI — `ValueError`, данные не сохраняются.
- Миграция `0003_modification_specs`. Тесты: `AIEnrichmentServiceTest`.

## Как проверить

- `docker compose exec backend python manage.py migrate`
- `docker compose exec backend python manage.py test core`
- В админке у модификации отображается поле «Характеристики (AI)»; после расчёта у выбранной модификации могут появиться/обновиться `specs` (Mock возвращает `engine_type: "V16 Diesel", year: 2020`).

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

## Когда будет API-ключ (Модуль 4 — переход с Mock на OpenAI)

1. **Файл создать:** `backend/core/services/ai/openai_client.py`  
   Класс `OpenAIClient(BaseAIClient)`, метод `get_model_specs(self, model_name: str) -> dict`: вызов OpenAI API (Chat Completions), парсинг JSON из ответа, возврат `{"engine_type": str, "year": int}`.

2. **Куда вставить ключ:** нигде в коде не хардкодить. Только в переменной окружения, например `OPENAI_API_KEY=sk-...`.

3. **Переменная окружения:** в `.env` на сервере и локально добавить:
   ```env
   OPENAI_API_KEY=sk-твой-ключ
   ```
   В коде читать: `os.environ.get("OPENAI_API_KEY")`; при отсутствии ключа не вызывать API (или использовать Mock).

4. **Docker:** в `docker-compose.yml` в секции `backend` в `environment` добавить:
   ```yaml
   OPENAI_API_KEY: ${OPENAI_API_KEY:-}
   ```
   В `.env.example` указать: `# OPENAI_API_KEY=sk-...`

5. **Что заменить в `enrichment.py`:** в начале файла вместо:
   ```python
   from .mock_client import MockAIClient
   ```
   подставлять клиента по флагу, например:
   ```python
   from django.conf import settings
   from .mock_client import MockAIClient
   from .openai_client import OpenAIClient
   client = OpenAIClient() if getattr(settings, 'OPENAI_API_KEY', None) or os.environ.get('OPENAI_API_KEY') else MockAIClient()
   ```
   И в `AIEnrichmentService.__init__` использовать этот `client` по умолчанию, либо задать в настройках Django `AI_CLIENT_CLASS = 'core.services.ai.openai_client.OpenAIClient'` и инстанцировать его.

6. **Зависимости:** в `backend/requirements.txt` добавить `openai>=1.0`. Выполнить `pip install openai` / пересобрать образ.

7. **Пример prompt для строгого JSON:**  
   Системный/пользовательский промпт в духе:  
   «Ты возвращаешь только валидный JSON без markdown и комментариев. Формат: {"engine_type": "строка типа двигателя", "year": год выпуска (целое число)}. Модель техники: {model_name}.»  
   Использовать `response_format={"type": "json_object"}` в API, если поддерживается.

8. **Безопасный парсинг ответа:**  
   Получить строку ответа от API, затем:
   ```python
   import json
   text = response.choices[0].message.content.strip()
   if text.startswith("```"):
       text = text.split("```")[1].replace("json", "").strip()
   data = json.loads(text)
   _validate_specs(data)  # существующая валидация
   return {"engine_type": data["engine_type"], "year": int(data["year"])}
   ```
   Ошибки `json.JSONDecodeError` и `ValueError` из `_validate_specs` обрабатывать и пробрасывать `ValueError`, чтобы данные не сохранялись.

---
