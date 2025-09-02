from django.urls import path
from restaurant.views import restaurant_detail, contacts, about, reservation, get_available_times
from restaurant.apps import RestaurantConfig

app_name = RestaurantConfig.name

urlpatterns = [
    path('', restaurant_detail, name='restaurant_detail'),
    path('contacts/', contacts, name='contacts'),
    path('about/', about, name='about'),
    path('reservation/', reservation, name='reservation'),
    path('get-available-times/', get_available_times, name='get_available_times'),
]
