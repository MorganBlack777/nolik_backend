from waitress import serve
from main import app
import os

# Получаем порт из переменной окружения или используем 80 по умолчанию
port = int(os.environ.get("PORT", 80))

# Запускаем сервер
if __name__ == "__main__":
    print(f"Запуск сервера на порту {port}...")
    serve(app, host="0.0.0.0", port=port, threads=8) 