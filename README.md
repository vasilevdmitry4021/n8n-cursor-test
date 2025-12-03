# TORO Maintenance Orders API

REST API для управления заказами на техническое обслуживание и ремонт оборудования (ТОРО). Сервис реализован на Flask, использует SQLite и готов к локальному запуску.

## Требования
- Python 3.11+
- pip

## Установка
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Запуск
```bash
python app.py
# Приложение будет доступно на http://localhost:5000
```

## Структура проекта
- `app.py` — Flask-приложение, роуты и валидация
- `database.py` — инициализация SQLAlchemy и создание БД
- `models.py` — описание модели `Order`
- `requirements.txt` — зависимости
- `toro.db` — SQLite база данных (создаётся автоматически)

### Переменные окружения
- `TORO_DATABASE_URL` — переопределить путь к базе (по умолчанию `sqlite:///toro.db`). Пример: `export TORO_DATABASE_URL=sqlite:////tmp/toro.db`.
- `contact_email` теперь обязательное поле заказа; при обновлении схемы удалите старый `toro.db`, чтобы SQLAlchemy пересоздал таблицу с новым столбцом.

## Структура таблицы orders
| Поле             | Тип        | Описание                                   |
|------------------|------------|--------------------------------------------|
| id               | Integer PK | Уникальный идентификатор                   |
| order_number     | String     | Уникальный номер заказа TORO-YYYY-NNN      |
| equipment_type   | String     | Тип оборудования                           |
| equipment_id     | String     | Инвентарный номер                          |
| issue_description| Text       | Описание проблемы                          |
| priority         | String     | `low`, `medium`, `high` (по умолчанию medium) |
| status           | String     | `created`, `in_progress`, `completed` (по умолчанию created) |
| requester_name   | String     | ФИО заказчика                              |
| department       | String     | Отдел/цех                                  |
| contact_phone    | String     | Телефон `+7-XXX-XXX-XX-XX`                 |
| contact_email    | String     | Валидный email заказчика                   |
| created_at       | DateTime   | Дата создания                              |
| updated_at       | DateTime   | Дата обновления                            |

## Примеры использования API

### Создание заказа
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
        "contact_phone": "+7-911-222-33-44",
        "contact_email": "petrov@example.com"
      }'
```

### Получение всех заказов
```bash
curl http://localhost:5000/api/v1/orders
```

### Фильтрация заказов
```bash
curl "http://localhost:5000/api/v1/orders?priority=high&status=in_progress&department=Цех%20№1"
```

### Получение заказа по ID
```bash
curl http://localhost:5000/api/v1/orders/1
```

### Удаление заказа
```bash
curl -X DELETE http://localhost:5000/api/v1/orders/1
# Ответ 204 No Content при успешном удалении
```

## Логирование и CORS
- Все события пишутся в stdout в формате `timestamp | level | logger | message`. Создание заказа логируется уровнем INFO, ошибки — WARNING/ERROR.
- CORS открыт для всех доменов, что упрощает разработку фронтенда. Для продакшена ограничьте источники в `app.py`.

## Возможные ошибки
- `400 Bad Request` — невалидные данные или параметры фильтрации
- `404 Not Found` — заказ не найден
- `500 Internal Server Error` — внутренняя ошибка сервера или базы данных

### Что делать при ошибках
- Проверьте, что все обязательные поля заполнены и указаны корректные значения приоритета/статуса.
- Убедитесь, что телефон соответствует формату `+7-XXX-XXX-XX-XX`.
- Если ошибка 500 повторяется, удалите файл `toro.db`, чтобы пересоздать базу, или проверьте логи приложения.