import datetime
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect

from restaurant.forms import ReservationStep1Form, ReservationStep2Form, ReservationStep3Form
from .models import Restaurant, Table, Reservation
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse

def restaurant_detail(request):
    # Получаем активный ресторан (например, первый)
    restaurant = get_object_or_404(Restaurant, is_active=True)
    return render(request, 'restaurant/restaurant_detail.html', {'restaurant': restaurant})

def contacts(request):
    restaurant = Restaurant.objects.first()
    
    if request.method == 'POST':
        # Обработка формы
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        # Здесь можно добавить отправку email или сохранение в базу
        messages.success(request, 'Ваше сообщение отправлено! Мы свяжемся с вами в ближайшее время.')
        return redirect('restaurant:contacts')
    
    return render(request, 'restaurant/contacts.html', {'restaurant': restaurant})

def about(request):
    restaurant = Restaurant.objects.first()
    return render(request, 'restaurant/about.html', {'restaurant': restaurant})

def reservation(request):
    restaurant = Restaurant.objects.first()
    today = timezone.now().date()
    
    # Определяем текущий шаг из GET-параметра или сессии
    step = request.GET.get('step', '1')
    
    # Инициализируем переменные
    form = None
    available_hours = []
    reservation_data = request.session.get('reservation_data', {})
    show_success_modal = request.GET.get('success') == 'true'
    last_reservation = request.session.get('last_reservation', {})
    
    if request.method == 'POST':
        if step == '1':
            form = ReservationStep1Form(request.POST)
            if form.is_valid():
                # Сохраняем данные в сессии
                request.session['reservation_data'] = {
                    'date': form.cleaned_data['date'].isoformat(),
                    'time': form.cleaned_data['time'].strftime('%H:%M'),
                    'guests_count': form.cleaned_data['guests_count']
                }
                return redirect(reverse('restaurant:reservation') + '?step=2')
            else:
                # Если форма невалидна, показываем ошибки
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{form.fields[field].label}: {error}")
        
        elif step == '2':
            form = ReservationStep2Form(request.POST)
            if form.is_valid():
                # Обновляем данные в сессии
                reservation_data = request.session.get('reservation_data', {})
                reservation_data['table'] = form.cleaned_data['table'].id
                request.session['reservation_data'] = reservation_data
                return redirect(reverse('restaurant:reservation') + '?step=3')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{form.fields[field].label}: {error}")
        
        elif step == '3':
            form = ReservationStep3Form(request.POST)
            if form.is_valid():
                # Создаем бронирование
                reservation_data = request.session.get('reservation_data', {})
                reservation = form.save(commit=False)
                
                # Преобразуем строки обратно в нужные типы
                reservation.date = datetime.datetime.strptime(reservation_data.get('date'), '%Y-%m-%d').date()
                reservation.time = datetime.datetime.strptime(reservation_data.get('time'), '%H:%M').time()
                reservation.guests_count = reservation_data.get('guests_count')
                reservation.table_id = reservation_data.get('table')
                reservation.save()
                
                # Сохраняем данные брони для показа в модальном окне
                request.session['last_reservation'] = {
                    'date': reservation.date.isoformat(),
                    'time': reservation.time.strftime('%H:%M'),
                    'guests_count': reservation.guests_count,
                    'table_number': reservation.table.number,
                    'table_description': reservation.table.description,
                    'client_name': reservation.client_name,
                    'client_phone': reservation.client_phone,
                    'client_email': reservation.client_email,
                    'special_requests': reservation.special_requests,
                }
                
                # Очищаем сессию
                request.session.pop('reservation_data', None)
                
                # Перенаправляем на страницу с параметром успеха
                return redirect(reverse('restaurant:reservation') + '?success=true')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{form.fields[field].label}: {error}")
    
    # Обработка GET-запросов
    if step == '2':
        form = ReservationStep2Form()
        # Фильтруем столики по количеству гостей
        guests_count = int(reservation_data.get('guests_count', 1))
        form.fields['table'].queryset = Table.objects.filter(capacity__gte=guests_count)
        
        # Рассчитываем доступное время для выбранной даты
        date_str = reservation_data.get('date', '')
        if date_str:
            try:
                selected_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
                available_hours = calculate_available_times(selected_date, guests_count)
            except (ValueError, TypeError):
                available_hours = []
    elif step == '1':
        # Используем initial данные только если форма еще не была создана
        if form is None:
            form = ReservationStep1Form(initial=reservation_data)
        
        # Рассчитываем доступное время для выбранной даты
        date_str = reservation_data.get('date', '')
        guests_count = int(reservation_data.get('guests_count', 2))
        
        if date_str:
            try:
                selected_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
                available_hours = calculate_available_times(selected_date, guests_count)
            except (ValueError, TypeError):
                available_hours = []
    elif step == '3':
        if form is None:
            form = ReservationStep3Form()
    else:
        if form is None:
            form = ReservationStep1Form()
        step = '1'
    
    return render(request, 'restaurant/reservation.html', {
        'restaurant': restaurant,
        'today': today,
        'step': step,
        'form': form,
        'reservation_data': reservation_data,
        'show_success_modal': show_success_modal,
        'last_reservation': last_reservation,
        'available_hours': available_hours,
    })
def calculate_available_times(selected_date, guests_count):
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
@csrf_exempt
def get_available_times(request):
    if request.method == 'POST':
        date_str = request.POST.get('date')
        guests_count = int(request.POST.get('guests_count', 2))
        
        try:
            selected_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            available_hours = calculate_available_times(selected_date, guests_count)
            return JsonResponse({'available_hours': available_hours})
        except (ValueError, TypeError):
            return JsonResponse({'error': 'Invalid date format'}, status=400)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)