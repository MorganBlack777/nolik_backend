from main import app

# Для совместимости с Waitress
application = app

if __name__ == "__main__":
    # Этот файл используется для запуска приложения через WSGI-сервер
    # Например, через Gunicorn: gunicorn wsgi:app
    from waitress import serve
    serve(application, host="0.0.0.0", port=8000) 