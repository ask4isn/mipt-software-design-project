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
