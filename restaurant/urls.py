from django.urls import path

from restaurant.apps import RestaurantConfig
from restaurant.views import (AboutView, CancelReservationView, ContactsView,
                              EditReservationView, GetAvailableTimesView,
                              MyReservationsView, ReservationView,
                              RestaurantDetailView)

app_name = RestaurantConfig.name

urlpatterns = [
    path("", RestaurantDetailView.as_view(), name="restaurant_detail"),
    path("contacts/", ContactsView.as_view(), name="contacts"),
    path("about/", AboutView.as_view(), name="about"),
    path("reservation/", ReservationView.as_view(), name="reservation"),
    path(
        "get-available-times/",
        GetAvailableTimesView.as_view(),
        name="get_available_times",
    ),
    path("my-reservations/", MyReservationsView.as_view(), name="my_reservations"),
    path(
        "my-reservations/<int:pk>/edit/",
        EditReservationView.as_view(),
        name="edit_reservation",
    ),
    path(
        "my-reservations/<int:pk>/cancel/",
        CancelReservationView.as_view(),
        name="cancel_reservation",
    ),
]
