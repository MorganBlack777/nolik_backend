# Gunicorn configuration file
import multiprocessing

# Основные настройки
bind = "0.0.0.0:8000"  # Адрес и порт для прослушивания
workers = multiprocessing.cpu_count() * 2 + 1  # Количество рабочих процессов
worker_class = "uvicorn.workers.UvicornWorker"  # Используем Uvicorn worker для FastAPI
timeout = 120  # Таймаут в секундах
keepalive = 5  # Время в секундах для keep-alive соединений

# Логирование
accesslog = "access.log"  # Лог доступа
errorlog = "error.log"  # Лог ошибок
loglevel = "info"  # Уровень логирования

# Настройки процесса
daemon = False  # Запускать как демон (в фоновом режиме)
reload = False  # Автоматическая перезагрузка при изменении кода (для продакшена отключено)

# Безопасность
limit_request_line = 4094  # Ограничение длины строки запроса
limit_request_fields = 100  # Ограничение количества полей заголовка
limit_request_field_size = 8190  # Ограничение размера поля заголовка 