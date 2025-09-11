# Docker Commands

## Настройка .env файла
Создайте файл `.env` в корне проекта со следующим содержимым:
```
# Database settings (обязательно заполните!)
DB_NAME=your_database_name
DB_USER=your_username
DB_PASSWORD=your_password
DB_HOST=db
DB_PORT=5432

# Django settings
DEBUG=1
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
```

## Запуск проекта
```bash
docker-compose up --build
```

## Запуск в фоновом режиме
```bash
docker-compose up -d --build
```

## Остановка контейнеров
```bash
docker-compose down
```

## Создание суперпользователя
```bash
docker-compose exec web python manage.py createsuperuser --settings=myproject.docker_settings
```

## Выполнение миграций
```bash
docker-compose exec web python manage.py migrate --settings=myproject.docker_settings
```

## Сбор статических файлов
```bash
docker-compose exec web python manage.py collectstatic --noinput --settings=myproject.docker_settings
```

## Доступ к контейнеру
```bash
docker-compose exec web bash
```

## Просмотр логов
```bash
docker-compose logs web
```

## Очистка volumes (удаление базы данных)
```bash
docker-compose down -v
```
