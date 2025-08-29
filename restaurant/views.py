from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
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

@csrf_exempt
def reservation(request):
    restaurant = Restaurant.objects.first()
    today = timezone.now().date()
    
    if request.method == 'POST':
        try:
            # Получаем данные из запроса
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                # AJAX запрос
                client_name = request.POST.get('client_name')
                client_phone = request.POST.get('client_phone')
                client_email = request.POST.get('client_email', '')
                table_id = request.POST.get('table')
                date = request.POST.get('date')
                time = request.POST.get('time')
                guests_count = request.POST.get('guests_count')
                special_requests = request.POST.get('special_requests', '')
                
                # Создаем бронирование
                table = Table.objects.get(id=table_id)
                reservation = Reservation(
                    client_name=client_name,
                    client_phone=client_phone,
                    client_email=client_email,
                    table=table,
                    date=date,
                    time=time,
                    guests_count=guests_count,
                    special_requests=special_requests
                )
                reservation.save()
                
                # Возвращаем JSON ответ
                return JsonResponse({
                    'success': True,
                    'reservation': {
                        'date': date,
                        'time': time,
                        'guests_count': guests_count,
                        'table_number': table.number,
                        'table_description': table.description,
                        'client_name': client_name,
                        'client_phone': client_phone,
                        'client_email': client_email,
                        'special_requests': special_requests,
                    }
                })
            else:
                # Обычный POST запрос
                # Ваша существующая логика
                pass
                
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    # GET request - показываем форму
    # Генерируем доступные часы
    available_hours = []
    for hour in range(12, 23):
        available_hours.append({
            'time': f"{hour}:00",
            'available': True  # Здесь должна быть логика проверки доступности
        })
    
    # Получаем все столики
    tables = Table.objects.all()
    for table in tables:
        # Здесь должна быть логика проверки доступности столика
        table.available = True
    
    return render(request, 'restaurant/reservation.html', {
        'restaurant': restaurant,
        'today': today,
        'available_hours': available_hours,
        'tables': tables
    })