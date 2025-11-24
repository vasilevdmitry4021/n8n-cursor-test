# Спецификация API для системы ТОРО

## Описание
REST API для управления заказами на техническое обслуживание и ремонт оборудования.

## Технологический стек
- Python 3.11+
- Flask (минималистичный веб-фреймворк)
- SQLite (встроенная БД, не требует установки)

## Структура данных

### Order (Заказ)
- `id` - integer, автоинкремент, первичный ключ
- `order_number` - string, уникальный, формат "TORO-2025-001" (автогенерация)
- `equipment_type` - string, обязательное (тип оборудования)
- `equipment_id` - string, обязательное (инвентарный номер)
- `issue_description` - text, обязательное (описание проблемы)
- `priority` - string, enum: "low", "medium", "high", default="medium"
- `status` - string, enum: "created", "in_progress", "completed", default="created"
- `requester_name` - string, обязательное (ФИО заказчика)
- `department` - string, обязательное (отдел/цех)
- `contact_phone` - string, обязательное (контактный телефон)
- `created_at` - datetime, автоматически при создании
- `updated_at` - datetime, автоматически при обновлении

## Эндпоинты

### POST /api/v1/orders
Создать новый заказ

**Входные данные:**
```json
{
  "equipment_type": "Станок ЧПУ",
  "equipment_id": "CNC-001",
  "issue_description": "Проблема с системой охлаждения",
  "priority": "high",
  "requester_name": "Иванов Иван Иванович",
  "department": "Цех №1",
  "contact_phone": "+7-900-123-45-67"
}
```

**Ответ (201 Created):**
```json
{
  "id": 1,
  "order_number": "TORO-2025-001",
  "equipment_type": "Станок ЧПУ",
  "equipment_id": "CNC-001",
  "issue_description": "Проблема с системой охлаждения",
  "priority": "high",
  "status": "created",
  "requester_name": "Иванов Иван Иванович",
  "department": "Цех №1",
  "contact_phone": "+7-900-123-45-67",
  "created_at": "2025-11-24T15:30:00Z",
  "updated_at": "2025-11-24T15:30:00Z"
}
```

### GET /api/v1/orders
Получить список всех заказов

**Параметры запроса (опционально):**
- `priority` - фильтр по приоритету (low/medium/high)
- `status` - фильтр по статусу (created/in_progress/completed)

**Ответ (200 OK):**
```json
{
  "orders": [
    { /* объект Order */ },
    { /* объект Order */ }
  ],
  "total": 25
}
```

### GET /api/v1/orders/{id}
Получить конкретный заказ по ID

**Ответ (200 OK):** объект Order
**Ответ (404 Not Found):** если заказ не найден

## Требования к реализации

### Структура проекта

json
{
"equipment_type": "Станок ЧПУ",
"equipment_id": "CNC-001",
"issue_description": "Проблема с системой охлаждения",
"priority": "high",
"requester_name": "Иванов Иван Иванович",
"department": "Цех №1",
"contact_phone": "+7-900-123-45-67"
}



**Ответ (201 Created):**
```json
{
  "id": 1,
  "order_number": "TORO-2025-001",
  "equipment_type": "Станок ЧПУ",
  "equipment_id": "CNC-001",
  "issue_description": "Проблема с системой охлаждения",
  "priority": "high",
  "status": "created",
  "requester_name": "Иванов Иван Иванович",
  "department": "Цех №1",
  "contact_phone": "+7-900-123-45-67",
  "created_at": "2025-11-24T15:30:00Z",
  "updated_at": "2025-11-24T15:30:00Z"
}
Пример использования
После запуска должна быть возможность создать заказ через curl:
curl -X POST http://localhost:5000/api/v1/orders \  -H "Content-Type: application/json" \  -d '{    "equipment_type": "Токарный станок",    "equipment_id": "LAT-042",    "issue_description": "Не работает автоподача",    "priority": "medium",    "requester_name": "Петров П.П.",    "department": "Цех №2",    "contact_phone": "+7-911-222-33-44"  }
```
GET /api/v1/orders
Получить список всех заказов
Параметры запроса (опционально):
priority - фильтр по приоритету (low/medium/high)
status - фильтр по статусу (created/in_progress/completed)
Ответ (200 OK):

{
  "orders": [
    { /* объект Order */ },
    { /* объект Order */ }
  ],
  "total": 25
}a8625a82f26/followup \
  -u YOUR_API_KEY: \
  --header 'Content-Type: application/json' \
  --data '{
  "prompt": {
    "text": "Прочитай файл TORO_API_SPEC.md в корне репозитория и реализуй описанное в нём REST API. Создай все необходимые файлы (app.py, models.py, database.py, requirements.txt, README.md) с полным рабочим кодом. Следуй всем требованиям из спецификации."
  }
}'

GET /api/v1/orders/{id}
Получить конкретный заказ по ID
Ответ (200 OK): объект Order
Ответ (404 Not Found): если заказ не найден
Требования к реализации
Структура проекта
/├── app.py              # главный файл приложения├── models.py           # модели данных├── database.py         # инициализация БД├── requirements.txt    # зависимости└── README.md          # инструкции по запуску"Создай простое Flask REST API для заказов ТОРО (техобслуживание оборудования).\n\nСоздай эти файлы:\n\n1. app.py - Flask приложение с 3 эндпоинтами:\n   - POST /api/v1/orders - создать заказ\n   - GET /api/v1/orders - список заказов\n   - GET /api/v1/orders/<id> - получить заказ\n\n2. models.py - SQLAlchemy модель Order с полями: id, order_number (автогенерация TORO-2025-001), equipment_type, equipment_id, issue_description, priority (low/medium/high), status (created/in_progress/completed), requester_name, department, contact_phone, created_at, updated_at\n\n3. database.py - настройка SQLite\n\n4. requirements.txt - Flask==3.0.0, Flask-SQLAlchemy==3.1.1, Flask-CORS==4.0.0\n\n5. README.md - как установить (pip install -r requirements.txt) и запустить (python app.py), примеры curl запросов\n\nВесь код должен быть рабочим. Добавь валидацию данных, обработку ошибок, логирование, CORS."  }}'
Обязательные функции
Валидация входных данных (все обязательные поля должны быть заполнены)
Автогенерация номера заказа в формате TORO-YYYY-NNN
Обработка ошибок (400 для невалидных данных, 404 для не найденных ресурсов, 500 для серверных ошибок)
Логирование основных операций (создание заказа, ошибки)
CORS для возможности вызова из браузера
Пример использования
После запуска должна быть возможность создать заказ через curl:
curl -X POST http://localhost:5000/api/v1/orders \  -H "Content-Type: application/json" \  -d '{    "equipment_type": "Токарный станок",    "equipment_id": "LAT-042",    "issue_description": "Не работает автоподача",    "priority": "medium",    "requester_name": "Петров П.П.",    "department": "Цех №2",    "contact_phone": "+7-911-222-33-44"  }'
---### Шаг 2: Загрузите этот файл в GitHubМожете создать файл прямо через веб-интерфейс GitHub:1. Откройте https://github.com/vasilevdmitry4021/n8n-cursor-test2. Нажмите "Add file" → "Create new file"3. Имя файла: `TORO_API_SPEC.md`4. Вставьте содержимое выше5. Commit в `main` бранч---### Шаг 3: Отправьте followup запрос агентуТеперь агент сможет прочитать спецификацию из репозитория:```bashcurl --request POST \  --url https://api.cursor.com/v0/agents/bc-18b342a8-ce03-44ca-b863-5a8625a82f26/followup \  -u YOUR_API_KEY: \  --header 'Content-Type: application/json' \  --data '{  "prompt": {    "text": "Прочитай файл TORO_API_SPEC.md в корне репозитория и реализуй описанное в нём REST API. Создай все необходимые файлы (app.py, models.py, database.py, requirements.txt, README.md) с полным рабочим кодом. Следуй всем требованиям из спецификации."  }}'

