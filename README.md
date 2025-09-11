## Проект: Бронирование столиков в ресторане (Django)

Django-приложение для онлайн-бронирования столиков реализованный в 3 шага, кабинетом пользователя и формой обратной связи. Auth на кастомной модели пользователя, хранение медиа (аватарки, логотип/фасад ресторана), расчёт доступного времени и выбор свободных столов.

### Стек
- **Backend**: Django 5.2
- **DB**: PostgreSQL
- **Frontend**: Django templates + статические файлы (`restaurant/static`)
- **Контейнеры**: Docker, docker-compose

### Основные возможности
- Карточка ресторана и страницы «О нас», «Контакты»
- Мастер бронирования (дата/время/гости → выбор стола → контактные данные)
- Расчёт доступных слотов времени и столов с учётом пересечения брони (±2 часа)
- Личный кабинет: активные/прошлые брони, редактирование и отмена
- Регистрация/логин/профиль пользователя с аватаром
- Медиа: логотипы/фасады ресторана, файлы пользователей

### Структура URL
- `GET /` — карточка ресторана
- `GET /about/` — о нас
- `GET,POST /contacts/` — контакты + отправка сообщения
- `GET,POST /reservation/?step=1|2|3` — мастер бронирования
- `POST /get-available-times/` — доступные слоты времени (AJAX)
- `GET /my-reservations/` — мои бронирования (только авторизованные)
- `GET,POST /my-reservations/<id>/edit/` — редактировать бронь
- `POST /my-reservations/<id>/cancel/` — отменить бронь
- `GET,POST /users/register` — регистрация
- `GET,POST /users/login` — вход
- `POST /users/logout` — выход
- `GET,POST /users/profile` — профиль
- `GET /admin/` — админка

---

## Быстрый старт (Docker)

1) Создайте `.env` в корне:

```env
SECRET_KEY=change-me
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

DB_NAME=restaurant
DB_USER=postgres
DB_PASSWORD=postgres
DB_PORT=5432
DB_HOST=db
```

2) Запуск:

```bash
docker compose up -d --build
```

3) Примените миграции и создайте суперпользователя:

```bash
docker compose exec web python manage.py migrate --settings=myproject.docker_settings
docker compose exec web python manage.py createsuperuser --settings=myproject.docker_settings
```

4) Откройте `http://localhost:8000/`.

Медиа/статик монтируются в томе `media_volume` и `static_volume`.

---

## Локальный запуск (без Docker)

Текущие `myproject/settings.py` настроены на PostgreSQL. Нужен локальный Postgres.

1) Установите зависимости Python 3.11:

```bash
pip install -r requirements.txt
```

2) Поднимите PostgreSQL и создайте базу  (адаптируйте `DATABASES` в `myproject/settings.py`).

3) Миграции и суперпользователь:

```bash
python manage.py migrate
python manage.py csu (логин и пароль можно посмотреть в кастомной команде)
```

4) Запуск дев-сервера:

```bash
python manage.py runserver
```

Медиа доступны по `MEDIA_URL=/media/` (смонтируются в `./media`).

Примечание: если хотите быстро запустить без Postgres, временно смените в `myproject/settings.py` на SQLite:

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
```

---

## Переменные окружения (Docker)
- **SECRET_KEY**: секрет Django
- **DEBUG**: `True/False`
- **ALLOWED_HOSTS**: csv-список хостов
- **DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT**: доступ к Postgres

В Docker используется `myproject/docker_settings.py`, который читает `.env`.

---

## Данные и медиа
- Лого/фасады ресторанов: `media/restaurant_logos`, `media/restaurant_facades`
- Аватары пользователей: `media/users_avatar`
- Настройки путей: `MEDIA_URL=/media/`, `MEDIA_ROOT=media/`

---

## Где логика
- Модели: `restaurant/models.py` (`Restaurant`, `Table`, `Reservation`, `Feedback`)
- Вьюхи и мастер бронирования: `restaurant/views.py`
- Сервисы расчёта слотов/столов: `restaurant/services.py`
- Формы бронирования: `restaurant/forms.py`
- Пользователи и аутентификация: `users/*`

---

## Тестовые действия
1) Зайдите в `/admin/`, создайте `Restaurant` и `Table`(ы). Отметьте `is_active` у ресторана.
2) Пройдите мастер `/reservation/` шаги 1→3. Проверьте ограничения по времени (±2 часа) и вместимости.
3) Авторизуйтесь и проверьте `/my-reservations/`, редактирование/отмену.

---

## Полезные команды
```bash
# Миграции
python manage.py makemigrations
python manage.py migrate

# Создание суперпользователя
python manage.py createsuperuser

# Сборка статики (если понадобится)
python manage.py collectstatic --noinput
```

---

## Примечания
- В `docker-compose.yml` команда веб-сервиса запускает сервер без автопрогонки миграций. Выполните `migrate` вручную как указано выше.
- В dev-режиме `DEBUG=True`. В prod установите `DEBUG=False`, задайте надёжный `SECRET_KEY` и корректный `ALLOWED_HOSTS`.


