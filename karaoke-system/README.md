# Karaoke Bar Management System

## Технологии
- Python 3.9+
- FastAPI
- Uvicorn
- Pydantic

## Структура

app/
main.py # REST API
models.py # Модели предметной области
storage.py # Хранилище данных

## Запуск
```bash
uvicorn app.main:app --reload --port 8000
```
После запуска по адресу можно посмотреть на SwaggerUI:
http://127.0.0.1:8000/docs

## Запрос для кода ИИ:
На основе моих UML (Use Case, Class, Activity/Sequence) и требований из отчета сгенерируй каркас FastAPI-прототипа. Разделение на app/main.py, app/models.py, app/storage.py. В models.py должны быть pydantic модели. Статусы enum или Literal. storage.py: словари для rooms/bookings/sessions/queues/menu/orders/bill и функцию для пересечения временных интервалов, утилиты для выборки броней. main.py: чисто по RESTAPI. Если найдешь несоответствия, предложи минимальные правки. Демонстрация через Swagger.