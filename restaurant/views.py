from django.shortcuts import render, get_object_or_404, redirect
from .models import Restaurant
from django.contrib import messages

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

from django.utils import timezone

def reservation(request):
    restaurant = Restaurant.objects.first()
    today = timezone.now().date()
    
    if request.method == 'POST':
        # Обработка формы бронирования
        # Здесь будет логика сохранения бронирования в базу данных
        pass
    
    return render(request, 'restaurant/reservation.html', {
        'restaurant': restaurant,
        'today': today
    })