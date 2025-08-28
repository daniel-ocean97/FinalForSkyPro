from django.urls import path
from restaurant.views import restaurant_detail, contacts, about  # ← Новое представление
from restaurant.apps import RestaurantConfig

app_name = RestaurantConfig.name

urlpatterns = [
    path('', restaurant_detail, name='restaurant_detail'),
    path('contacts/', contacts, name='contacts'),
    path('about/', about, name='about'),
]
