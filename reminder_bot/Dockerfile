FROM python:3.11-slim

WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода
COPY . .

# Создание папки для временных файлов
RUN mkdir -p /tmp

# Запуск через functions-framework (для вебхуков)
CMD ["functions-framework", "--target=app", "--source=main.py", "--port=8080"]