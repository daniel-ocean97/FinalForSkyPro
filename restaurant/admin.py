from django.contrib import admin

from .models import Feedback, Reservation, Restaurant, Table


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ["name", "address", "rating", "is_active"]
    search_fields = ["name", "address"]


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ["number", "description", "is_active"]
    search_fields = ["number", "description"]


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ["client_name", "client_phone", "date"]
    search_fields = ["client_name", "date"]


admin.site.register(Feedback)
