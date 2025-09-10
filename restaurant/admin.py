from django.contrib import admin
from .models import Restaurant, Table, Reservation, Feedback

@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ['name', 'address', 'rating', 'is_active']
    search_fields = ['name', 'address']

@admin.register(Table)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ['number', 'description', 'is_active']
    search_fields = ['number', 'description']

@admin.register(Reservation)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ['client_name', 'client_phone', 'date']
    search_fields = ['client_name', 'date']

admin.site.register(Feedback)
