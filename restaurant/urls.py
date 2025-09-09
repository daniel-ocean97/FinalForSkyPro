from django.urls import path
from restaurant.views import restaurant_detail, contacts, about, reservation, get_available_times, my_reservations, edit_reservation, cancel_reservation
from restaurant.apps import RestaurantConfig

app_name = RestaurantConfig.name

urlpatterns = [
    path('', restaurant_detail, name='restaurant_detail'),
    path('contacts/', contacts, name='contacts'),
    path('about/', about, name='about'),
    path('reservation/', reservation, name='reservation'),
    path('get-available-times/', get_available_times, name='get_available_times'),
    path('my-reservations/', my_reservations, name='my_reservations'),
    path('my-reservations/<int:pk>/edit/', edit_reservation, name='edit_reservation'),
    path('my-reservations/<int:pk>/cancel/', cancel_reservation, name='cancel_reservation'),
]
