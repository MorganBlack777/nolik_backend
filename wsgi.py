from main import app
from uvicorn.adapters.wsgi import WSGIMiddleware

# Создаем WSGI-приложение из ASGI-приложения FastAPI
application = WSGIMiddleware(app)

# Для совместимости с Waitress
app = application

if __name__ == "__main__":
    # Этот файл используется для запуска приложения через WSGI-сервер
    # Например, через Gunicorn: gunicorn wsgi:app
    from waitress import serve
    serve(application, host="0.0.0.0", port=8000) 