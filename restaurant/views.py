import datetime
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect

from restaurant.forms import ReservationStep1Form, ReservationStep2Form, ReservationStep3Form
from .models import Restaurant, Table, Reservation
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt


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
    
    if request.method == 'POST':
        step = request.POST.get('step', '1')
        
        if step == '1':
            form = ReservationStep1Form(request.POST)
            if form.is_valid():
                # Сохраняем данные в сессии
                request.session['reservation_data'] = {
                    'date': form.cleaned_data['date'].isoformat(),
                    'time': form.cleaned_data['time'].isoformat(),
                    'guests_count': form.cleaned_data['guests_count']
                }
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'errors': form.errors.get_json_data()})
                
        elif step == '2':
            form = ReservationStep2Form(request.POST)
            if form.is_valid():
                request.session['reservation_data']['table'] = form.cleaned_data['table'].id
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'errors': form.errors})
                
        elif step == '3':
            form = ReservationStep3Form(request.POST)
            if form.is_valid():
                # Создаем бронирование
                reservation_data = request.session.get('reservation_data', {})
                reservation = form.save(commit=False)
                reservation.table_id = reservation_data.get('table')
                reservation.date = reservation_data.get('date')
                reservation.time = reservation_data.get('time')
                reservation.guests_count = reservation_data.get('guests_count')
                reservation.save()
                
                # Очищаем сессию
                request.session.pop('reservation_data', None)
                
                return JsonResponse({
                    'success': True,
                    'reservation': {
                        'date': reservation.date.strftime('%Y-%m-%d'),
                        'time': reservation.time.strftime('%H:%M'),
                        'guests_count': reservation.guests_count,
                        'table_number': reservation.table.number,
                        'table_description': reservation.table.description,
                        'client_name': reservation.client_name,
                        'client_phone': reservation.client_phone,
                        'client_email': reservation.client_email,
                        'special_requests': reservation.special_requests,
                    }
                })
            else:
                return JsonResponse({'success': False, 'errors': form.errors})
    
    # GET request - показываем форму
    # Для шага 2 нужно динамически установить queryset для выбора столиков
    step2_form = ReservationStep2Form()
    reservation_data = request.session.get('reservation_data', {})
    
    if reservation_data:
        # Фильтруем столики по количеству гостей и доступности
        tables = Table.objects.filter(capacity__gte=reservation_data.get('guests_count', 1))
        step2_form.fields['table'].queryset = tables
    
    return render(request, 'restaurant/reservation.html', {
        'restaurant': restaurant,
        'today': today,
        'step1_form': ReservationStep1Form(),
        'step2_form': step2_form,
        'step3_form': ReservationStep3Form()
    })

@csrf_exempt
def get_available_times(request):
    if request.method == 'POST':
        date_str = request.POST.get('date')
        guests_count = int(request.POST.get('guests_count', 2))
        
        try:
            selected_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            return JsonResponse({'error': 'Invalid date format'}, status=400)
        
        # Проверяем, что дата не в прошлом
        today = timezone.now().date()
        if selected_date < today:
            return JsonResponse({'available_hours': []})
        
        # Если дата сегодня, то нужно учитывать текущее время
        now = timezone.now()
        current_time = now.time()
        
        # Часы работы ресторана
        opening_time = datetime.time(10, 0)
        closing_time = datetime.time(22, 0)
        
        # Получаем подходящие столики по вместимости
        tables = Table.objects.filter(capacity__gte=guests_count)
        
        # Получаем все активные бронирования на выбранную дату
        active_reservations = Reservation.objects.filter(
            date=selected_date,
            status__in=['pending', 'confirmed']
        )
        
        # Создаем множество занятых временных слотов
        busy_slots = set()
        for reservation in active_reservations:
            # Добавляем время бронирования в занятые слоты
            busy_slots.add(reservation.time.strftime('%H:%M'))
            
            # Если бронирование длится 2 часа, добавляем следующий час
            # (замените эту логику, если у вас есть поле длительности)
            next_hour = (datetime.datetime.combine(selected_date, reservation.time) + 
                        datetime.timedelta(hours=1)).time()
            busy_slots.add(next_hour.strftime('%H:%M'))
        
        available_hours = []
        current_slot = opening_time
        
        # Проверяем каждый временной слот
        while current_slot < closing_time:
            # Если дата сегодня и текущий слот уже прошел, пропускаем
            if selected_date == today and current_slot < current_time:
                available_hours.append({
                    'time': current_slot.strftime('%H:%M'),
                    'available': False
                })
            else:
                # Проверяем, есть ли свободные столики для этого временного слота
                slot_str = current_slot.strftime('%H:%M')
                
                # Если слот занят в любом столике, отмечаем как недоступный
                is_available = slot_str not in busy_slots
                
                available_hours.append({
                    'time': slot_str,
                    'available': is_available
                })
            
            # Переходим к следующему слоту
            current_slot = (datetime.datetime.combine(selected_date, current_slot) + 
                           datetime.timedelta(hours=1)).time()
        
        return JsonResponse({'available_hours': available_hours})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)