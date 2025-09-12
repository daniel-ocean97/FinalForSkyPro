# restaurant/services.py
import datetime

from django.utils import timezone

from .models import Reservation, Restaurant, Table


def calculate_available_times(selected_date, guests_count):
    """
    Рассчитывает доступное время для бронирования на указанную дату
    """
    now = timezone.now()
    today = now.date()

    if selected_date < today:
        return []

    current_time = now.time()
    opening_time = datetime.time(10, 0)
    closing_time = datetime.time(22, 0)

    tables = Table.objects.filter(capacity__gte=guests_count)
    active_reservations = Reservation.objects.filter(
        date=selected_date, status__in=["pending", "confirmed"]
    )

    busy_tables_by_time = {}
    for reservation in active_reservations:
        time_str = reservation.time.strftime("%H:%M")
        if time_str not in busy_tables_by_time:
            busy_tables_by_time[time_str] = set()
        busy_tables_by_time[time_str].add(reservation.table_id)

        next_hour = (
            datetime.datetime.combine(selected_date, reservation.time)
            + datetime.timedelta(hours=2)
        ).time()
        next_hour_str = next_hour.strftime("%H:%M")
        if next_hour_str not in busy_tables_by_time:
            busy_tables_by_time[next_hour_str] = set()
        busy_tables_by_time[next_hour_str].add(reservation.table_id)

    available_hours = []
    current_slot = opening_time

    while current_slot < closing_time:
        slot_str = current_slot.strftime("%H:%M")

        if selected_date == today and current_slot < current_time:
            available_hours.append({"time": slot_str, "available": False})
        else:
            busy_tables = busy_tables_by_time.get(slot_str, set())
            available_tables = tables.exclude(id__in=busy_tables)
            is_available = available_tables.exists()

            available_hours.append({"time": slot_str, "available": is_available})

        current_slot = (
            datetime.datetime.combine(selected_date, current_slot)
            + datetime.timedelta(hours=1)
        ).time()

    return available_hours


def get_available_tables(selected_date, selected_time, guests_count):
    """
    Возвращает доступные столики для указанной даты, времени и количества гостей
    """
    # Получаем подходящие столики по вместимости
    tables = Table.objects.filter(capacity__gte=guests_count)

    # Получаем все активные бронирования на выбранную дату
    active_reservations = Reservation.objects.filter(
        date=selected_date, status__in=["pending", "confirmed"]
    )

    # Создаем множество занятых столиков на выбранное время
    busy_tables = set()

    for reservation in active_reservations:
        # Проверяем пересечение временных интервалов
        reservation_start = datetime.datetime.combine(selected_date, reservation.time)
        reservation_end = reservation_start + datetime.timedelta(
            hours=2
        )  # Бронь на 2 часа

        selected_start = datetime.datetime.combine(selected_date, selected_time)
        selected_end = selected_start + datetime.timedelta(hours=2)

        # Если временные интервалы пересекаются, столик занят
        if reservation_start < selected_end and reservation_end > selected_start:
            busy_tables.add(reservation.table_id)

    # Добавляем флаг доступности к каждому столику
    for table in tables:
        table.available = table.id not in busy_tables

    return tables


# --------- Helpers extracted for views readability ---------


def get_active_restaurant():
    """
    Возвращает активный ресторан если есть, иначе первый попавшийся.
    """
    restaurant = Restaurant.objects.filter(is_active=True).first()
    if restaurant is None:
        restaurant = Restaurant.objects.first()
    return restaurant


def compute_available_hours_for_step1(date_value, guests_count, today):
    """
    Универсальная обертка для расчета доступных часов на шаге 1.
    Принимает дату (date/str/None) и возвращает список часов с флагом доступности.
    """
    try:
        if date_value:
            if isinstance(date_value, datetime.date):
                selected_date = date_value
            else:
                selected_date = datetime.datetime.strptime(
                    str(date_value), "%Y-%m-%d"
                ).date()
        else:
            selected_date = today
        return calculate_available_times(selected_date, int(guests_count or 2))
    except (ValueError, TypeError):
        return []


def format_display_date_ru(date_str):
    """
    Форматирует дату YYYY-MM-DD в строку вроде "15 мая" для отображения.
    Возвращает исходную строку при ошибке.
    """
    if not date_str:
        return ""
    try:
        date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        months = {
            1: "января",
            2: "февраля",
            3: "марта",
            4: "апреля",
            5: "мая",
            6: "июня",
            7: "июля",
            8: "августа",
            9: "сентября",
            10: "октября",
            11: "ноября",
            12: "декабря",
        }
        return f"{date_obj.day} {months[date_obj.month]}"
    except (ValueError, TypeError):
        return date_str


def get_table_number_safe(table_id):
    """Возвращает номер столика по id или дефолтную строку."""
    if not table_id:
        return ""
    try:
        table = Table.objects.get(id=table_id)
        return table.number
    except Table.DoesNotExist:
        return "Неизвестный столик"
