FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Копируем файлы зависимостей
COPY requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код проекта
COPY . .

# Создаем директории для статических файлов и медиа
RUN mkdir -p /app/static /app/media

# Открываем порт
EXPOSE 8000

# Команда запуска
CMD ["sh", "-c", "python manage.py migrate --settings=myproject.docker_settings && python manage.py runserver 0.0.0.0:8000 --settings=myproject.docker_settings"]
