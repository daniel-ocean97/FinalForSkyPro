# restaurant/services.py
import datetime
from django.utils import timezone
from .models import Table, Reservation

def calculate_available_times(selected_date, guests_count):
    """
    Рассчитывает доступное время для бронирования на указанную дату
    """
    today = timezone.now().date()
    if selected_date < today:
        return []

    now = timezone.now()
    current_time = now.time()
    opening_time = datetime.time(10, 0)
    closing_time = datetime.time(22, 0)

    tables = Table.objects.filter(capacity__gte=guests_count)
    active_reservations = Reservation.objects.filter(
        date=selected_date,
        status__in=['pending', 'confirmed']
    )

    busy_tables_by_time = {}
    for reservation in active_reservations:
        time_str = reservation.time.strftime('%H:%M')
        if time_str not in busy_tables_by_time:
            busy_tables_by_time[time_str] = set()
        busy_tables_by_time[time_str].add(reservation.table_id)
        
        next_hour = (datetime.datetime.combine(selected_date, reservation.time) + 
                    datetime.timedelta(hours=1)).time()
        next_hour_str = next_hour.strftime('%H:%M')
        if next_hour_str not in busy_tables_by_time:
            busy_tables_by_time[next_hour_str] = set()
        busy_tables_by_time[next_hour_str].add(reservation.table_id)

    available_hours = []
    current_slot = opening_time

    while current_slot < closing_time:
        slot_str = current_slot.strftime('%H:%M')
        
        if selected_date == today and current_slot < current_time:
            available_hours.append({
                'time': slot_str,
                'available': False
            })
        else:
            busy_tables = busy_tables_by_time.get(slot_str, set())
            available_tables = tables.exclude(id__in=busy_tables)
            is_available = available_tables.exists()

            available_hours.append({
                'time': slot_str,
                'available': is_available
            })
        
        current_slot = (datetime.datetime.combine(selected_date, current_slot) + 
                       datetime.timedelta(hours=1)).time()

    return available_hours


def get_available_tables(selected_date, selected_time, guests_count):
    """
    Возвращает доступные столики для указанной даты, времени и количества гостей
    """
    # Получаем подходящие столики по вместимости
    tables = Table.objects.filter(capacity__gte=guests_count)
    
    # Получаем все активные бронирования на выбранную дату
    active_reservations = Reservation.objects.filter(
        date=selected_date,
        status__in=['pending', 'confirmed']
    )
    
    # Создаем множество занятых столиков на выбранное время
    busy_tables = set()
    
    for reservation in active_reservations:
        # Проверяем пересечение временных интервалов
        reservation_start = datetime.datetime.combine(
            selected_date, 
            reservation.time
        )
        reservation_end = reservation_start + datetime.timedelta(hours=2)  # Бронь на 2 часа
        
        selected_start = datetime.datetime.combine(selected_date, selected_time)
        selected_end = selected_start + datetime.timedelta(hours=2)
        
        # Если временные интервалы пересекаются, столик занят
        if (reservation_start < selected_end and reservation_end > selected_start):
            busy_tables.add(reservation.table_id)
    
    # Добавляем флаг доступности к каждому столику
    for table in tables:
        table.available = table.id not in busy_tables
    
    return tables