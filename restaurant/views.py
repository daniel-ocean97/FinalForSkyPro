from django.shortcuts import render, get_object_or_404
from .models import Restaurant

def restaurant_detail(request):
    # Получаем активный ресторан (например, первый)
    restaurant = get_object_or_404(Restaurant, is_active=True)
    return render(request, 'restaurant/restaurant_detail.html', {'restaurant': restaurant})
