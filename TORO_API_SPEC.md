# Спецификация API для системы ТОРО

## Описание
REST API для управления заказами на техническое обслуживание и ремонт оборудования (ТОРО).

## Технологический стек
- Python 3.11+
- Flask (минималистичный веб-фреймворк)
- SQLite (встроенная БД, не требует установки)
- Flask-SQLAlchemy для ORM
- Flask-CORS для поддержки CORS

## Структура данных

### Order (Заказ)
- `id` - integer, автоинкремент, первичный ключ
- `order_number` - string, уникальный, формат "TORO-2025-001" (автогенерация)
- `equipment_type` - string, обязательное (тип оборудования, например: "Станок ЧПУ", "Конвейер")
- `equipment_id` - string, обязательное (инвентарный номер, например: "CNC-001")
- `issue_description` - text, обязательное (подробное описание проблемы)
- `priority` - string, enum: "low", "medium", "high", default="medium"
- `status` - string, enum: "created", "in_progress", "completed", default="created"
- `requester_name` - string, обязательное (ФИО заказчика)
- `department` - string, обязательное (отдел/цех)
- `contact_phone` - string, обязательное (контактный телефон в формате +7-XXX-XXX-XX-XX)
- `contact_email` - string, обязательное (валидный email заявителя)
- `created_at` - datetime, автоматически при создании
- `updated_at` - datetime, автоматически при обновлении

## Эндпоинты API

### POST /api/v1/orders
Создать новый заказ на обслуживание/ремонт

**Входные данные (JSON):**
```json
{
  "equipment_type": "Станок ЧПУ",
  "equipment_id": "CNC-001",
  "issue_description": "Проблема с системой охлаждения. Температура превышает норму на 15 градусов.",
  "priority": "high",
  "requester_name": "Иванов Иван Иванович",
  "department": "Цех №1",
  "contact_phone": "+7-900-123-45-67",
  "contact_email": "ivanov@example.com"
}
```

**Успешный ответ (201 Created):**
```json
{
  "id": 1,
  "order_number": "TORO-2025-001",
  "equipment_type": "Станок ЧПУ",
  "equipment_id": "CNC-001",
  "issue_description": "Проблема с системой охлаждения. Температура превышает норму на 15 градусов.",
  "priority": "high",
  "status": "created",
  "requester_name": "Иванов Иван Иванович",
  "department": "Цех №1",
  "contact_phone": "+7-900-123-45-67",
  "contact_email": "ivanov@example.com",
  "created_at": "2025-11-24T15:30:00Z",
  "updated_at": "2025-11-24T15:30:00Z"
}
```

**Ошибки:**
- `400 Bad Request` - если не указаны обязательные поля или данные невалидны
- `500 Internal Server Error` - при ошибке сервера

---

### GET /api/v1/orders
Получить список всех заказов с возможностью фильтрации

**Параметры запроса (query params, все опциональны):**
- `priority` - фильтр по приоритету (low/medium/high)
- `status` - фильтр по статусу (created/in_progress/completed)
- `department` - фильтр по отделу

**Примеры запросов:**
```bash
# Все заказы
GET /api/v1/orders

# Только высокоприоритетные
GET /api/v1/orders?priority=high

# Заказы в работе из Цеха №1
GET /api/v1/orders?status=in_progress&department=Цех №1
```

**Успешный ответ (200 OK):**
```json
{
  "orders": [
    {
      "id": 1,
      "order_number": "TORO-2025-001",
      "equipment_type": "Станок ЧПУ",
      "equipment_id": "CNC-001",
      "issue_description": "Проблема с системой охлаждения",
      "priority": "high",
      "status": "created",
      "requester_name": "Иванов И.И.",
      "department": "Цех №1",
      "contact_phone": "+7-900-123-45-67",
      "contact_email": "ivanov@example.com",
      "created_at": "2025-11-24T15:30:00Z",
      "updated_at": "2025-11-24T15:30:00Z"
    },
    {
      "id": 2,
      "order_number": "TORO-2025-002",
      "equipment_type": "Конвейер",
      "equipment_id": "CONV-012",
      "issue_description": "Не работает приводной мотор",
      "priority": "medium",
      "status": "in_progress",
      "requester_name": "Петров П.П.",
      "department": "Цех №2",
      "contact_phone": "+7-911-222-33-44",
      "contact_email": "petrov@example.com",
      "created_at": "2025-11-24T16:00:00Z",
      "updated_at": "2025-11-24T16:15:00Z"
    }
  ],
  "total": 2
}
```

---

### GET /api/v1/orders/{id}
Получить конкретный заказ по ID

**Параметры пути:**
- `id` - integer, ID заказа

**Пример:**
```bash
GET /api/v1/orders/1
```

**Успешный ответ (200 OK):**
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
  "contact_email": "ivanov@example.com",
  "created_at": "2025-11-24T15:30:00Z",
  "updated_at": "2025-11-24T15:30:00Z"
}
```

**Ошибки:**
- `404 Not Found` - если заказ с указанным ID не существует

---

### DELETE /api/v1/orders/{id}
Удалить заказ, когда он больше не требуется.

**Параметры пути:**
- `id` - integer, ID заказа

**Пример:**
```bash
DELETE /api/v1/orders/1
```

**Успешный ответ (204 No Content):**
- Тело ответа отсутствует

**Ошибки:**
- `404 Not Found` - если заказ не существует
- `500 Internal Server Error` - если произошла ошибка базы данных

---

## Требования к реализации

### Структура проекта
```
/
├── app.py              # главный файл Flask приложения с роутами
├── models.py           # SQLAlchemy модели (Order)
├── database.py         # инициализация и настройка БД
├── requirements.txt    # Python зависимости
├── README.md          # документация по запуску и использованию
└── toro.db            # SQLite база данных (создается автоматически)
```

### Обязательные функции

1. **Валидация входных данных**
   - Все обязательные поля должны быть заполнены
   - Приоритет только из списка: low, medium, high
   - Статус только из списка: created, in_progress, completed
   - Телефон должен соответствовать формату

2. **Автогенерация номера заказа**
   - Формат: TORO-YYYY-NNN
   - YYYY - текущий год
   - NNN - порядковый номер (001, 002, и т.д.)
   - Пример: TORO-2025-001

3. **Обработка ошибок**
   - 400 Bad Request - невалидные данные
   - 404 Not Found - ресурс не найден
   - 500 Internal Server Error - ошибки сервера
   - Все ошибки должны возвращать JSON с описанием

4. **Логирование**
   - Логировать создание заказов
   - Логировать ошибки с деталями
   - Использовать стандартный модуль logging

5. **CORS поддержка**
   - Разрешить запросы из любых источников (для разработки)
   - Использовать Flask-CORS

### Пример использования после запуска

**Создание заказа:**
```bash
curl -X POST http://localhost:5000/api/v1/orders \
  -H "Content-Type: application/json" \
  -d '{
    "equipment_type": "Токарный станок",
    "equipment_id": "LAT-042",
    "issue_description": "Не работает автоматическая подача резца",
    "priority": "medium",
    "requester_name": "Петров Петр Петрович",
    "department": "Цех №2",
    "contact_phone": "+7-911-222-33-44"
  }'
```

**Получение всех заказов:**
```bash
curl http://localhost:5000/api/v1/orders
```

**Получение заказов с высоким приоритетом:**
```bash
curl "http://localhost:5000/api/v1/orders?priority=high"
```

**Получение конкретного заказа:**
```bash
curl http://localhost:5000/api/v1/orders/1
```

---

## Зависимости (requirements.txt)

Минимальный набор:
```
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Flask-CORS==4.0.0
```

---

## README.md должен содержать

1. Описание проекта
2. Требования (Python 3.11+)
3. Установка зависимостей (`pip install -r requirements.txt`)
4. Запуск приложения (`python app.py`)
5. Примеры использования API (curl команды)
6. Структура базы данных
7. Возможные ошибки и их решения

---

## Дополнительные требования

- Код должен быть **полностью рабочим** и готовым к запуску
- Использовать **best practices** Python/Flask
- Добавить **комментарии** к важным участкам кода
- База данных создается **автоматически** при первом запуске
- Приложение должно запускаться **на порту 5000**
- Все ответы API в формате **JSON**

