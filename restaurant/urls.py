from django.urls import path
from restaurant.views import restaurant_detail  # ← Новое представление
from restaurant.apps import RestaurantConfig

app_name = RestaurantConfig.name

urlpatterns = [
    path('', restaurant_detail, name='restaurant_detail'),  # Главная страница — детали ресторана
]
