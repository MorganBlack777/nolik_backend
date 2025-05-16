# Крестики-нолики (Tic-Tac-Toe) Backend

Бэкенд для игры "Крестики-нолики" с возможностью игры против бота или другого игрока.

## Особенности

- Игра "Крестики-нолики" с настраиваемым размером поля
- Игра против бота с разными уровнями сложности
- Игра против других игроков
- Аутентификация пользователей
- REST API для интеграции с фронтендом
- Веб-интерфейс для игры

## Технологии

- FastAPI
- SQLAlchemy
- Jinja2 Templates
- JWT Authentication
- Uvicorn/Gunicorn для развертывания

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/ваш_логин/nolik_backend.git
cd nolik_backend
```

2. Создайте виртуальное окружение и установите зависимости:
```bash
python -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Настройте переменные окружения (опционально):
```bash
cp .env.example .env
# Отредактируйте .env файл с вашими настройками
```

## Запуск

### Для разработки

```bash
uvicorn main:app --reload
```

### Для продакшена

#### На Linux/macOS:
```bash
gunicorn wsgi:app -c gunicorn_config.py
```

#### На Windows:
```bash
# Вариант 1: Через BAT-файл
run_server.bat

# Вариант 2: Напрямую через Waitress
waitress-serve --host=0.0.0.0 --port=80 wsgi:application

# Вариант 3: Через Python-скрипт
python waitress_serve.py
```

или

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## API Endpoints

- `GET /docs` - Swagger документация API
- `GET /redoc` - ReDoc документация API
- `POST /api/auth/token` - Получение токена авторизации
- `POST /api/users/` - Регистрация нового пользователя
- `GET /api/users/me` - Информация о текущем пользователе
- `GET /api/games/` - Список игр пользователя
- `POST /api/games/` - Создание новой игры
- `GET /api/games/{game_id}` - Получение информации об игре
- `POST /api/games/{game_id}/moves` - Сделать ход

## Веб-интерфейс

- `/` - Главная страница
- `/login` - Страница входа
- `/register` - Страница регистрации
- `/games` - Список игр
- `/games/new` - Создание новой игры
- `/games/{game_id}` - Страница игры

## Лицензия

MIT 