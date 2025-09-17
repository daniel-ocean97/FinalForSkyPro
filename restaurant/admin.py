from django.contrib import admin

from .models import Dish, DishCategory, Feedback, Reservation, Restaurant, Table


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


@admin.register(DishCategory)
class DishCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "order", "is_visible"]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name"]
    list_filter = ["is_visible"]


@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "price", "is_vegetarian", "is_spicy", "is_available"]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name", "description", "ingredients"]
    list_filter = ["category", "is_vegetarian", "is_spicy", "is_special", "is_available"]
