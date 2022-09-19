## Main-Service

### Локальная разрабока

Необходимо в системе иметь python3.10, pipenv, docker-compose.
1. Запустить docker-compose.dev:
```docker-compose -f docker-compose.dev.yml up --build```
2. Установить зависимости: `pipenv install --dev`
3. Зайти в виртуальное окружение: `pipenv shell`
4. Загрузить миграции в бд: `alembic upgrade head`

Для запуска тестов: `pytest`

Для запуска flake8: `flake8`

Для запуска mypy: `mypy`. Предварительно может быть необходима выполненна комманда: `mypy --install-types`

Для запуска сервера: `uvicorn src.views:app --reload `

Документаци API по адресу: `localhost:8000/docs`

### Развёртка сервера
Необходимо в системе иметь docker-compose.

1. Запустить docker-compose:
```docker-compose -f docker-compose.yml up --build```

2. Дождаться стабильного запуска main-service (Сервис RabbitMQ запускается быстро, но долго производит кофигурации, соответственно main-service будет падать, пока RabbitMQ не завершит настройку)

### Дополнительно
Файлы `.env` и `.docker.env` оставленны намеренно. Естественно, в реальных проектах пушить их нельзя.
