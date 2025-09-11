from django.urls import path

from restaurant.apps import RestaurantConfig
from restaurant.views import (about, cancel_reservation, contacts,
                              edit_reservation, get_available_times,
                              my_reservations, reservation, restaurant_detail)

app_name = RestaurantConfig.name

urlpatterns = [
    path("", restaurant_detail, name="restaurant_detail"),
    path("contacts/", contacts, name="contacts"),
    path("about/", about, name="about"),
    path("reservation/", reservation, name="reservation"),
    path("get-available-times/", get_available_times, name="get_available_times"),
    path("my-reservations/", my_reservations, name="my_reservations"),
    path("my-reservations/<int:pk>/edit/", edit_reservation, name="edit_reservation"),
    path(
        "my-reservations/<int:pk>/cancel/",
        cancel_reservation,
        name="cancel_reservation",
    ),
]
