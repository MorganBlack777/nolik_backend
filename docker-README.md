# Запуск проекта "Крестики-нолики" в Docker

## Предварительные требования

1. Установленный Docker: [https://docs.docker.com/get-docker/](https://docs.docker.com/get-docker/)
2. Установленный Docker Compose: [https://docs.docker.com/compose/install/](https://docs.docker.com/compose/install/)

## Запуск приложения

### Используя Docker Compose (рекомендуется)

1. Перейдите в корневую директорию проекта:
   ```
   cd /путь/к/проекту/nolik_backend
   ```

2. Запустите приложение с помощью Docker Compose:
   ```
   docker-compose up -d
   ```

3. Приложение будет доступно по адресу: [http://localhost:8000](http://localhost:8000)

4. Для остановки приложения выполните:
   ```
   docker-compose down
   ```

### Используя Docker напрямую

1. Соберите Docker образ:
   ```
   docker build -t tictactoe-app .
   ```

2. Запустите контейнер:
   ```
   docker run -d -p 8000:8000 -v $(pwd)/tictactoe.db:/app/tictactoe.db --name tictactoe tictactoe-app
   ```

3. Приложение будет доступно по адресу: [http://localhost:8000](http://localhost:8000)

4. Для остановки контейнера выполните:
   ```
   docker stop tictactoe
   docker rm tictactoe
   ```

## Важные замечания

1. База данных SQLite (tictactoe.db) монтируется как том, чтобы сохранять данные между перезапусками контейнера.

2. Если вы хотите изменить секретный ключ для JWT-токенов, отредактируйте переменную окружения `SECRET_KEY` в файле `docker-compose.yml`.

3. Для разработки можно включить режим горячей перезагрузки, изменив в `docker-compose.yml`:
   ```yaml
   command: ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
   ```
   и добавив монтирование исходного кода:
   ```yaml
   volumes:
     - ./tictactoe.db:/app/tictactoe.db
     - ./app:/app/app
     - ./main.py:/app/main.py
   ``` 