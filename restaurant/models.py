from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Restaurant(models.Model):
    # Основные поля
    name = models.CharField(max_length=100, verbose_name="Название")
    address = models.CharField(max_length=200, verbose_name="Адрес")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    
    # Дополнительные поля
    description = models.TextField(blank=True, verbose_name="Описание")
    opening_hours = models.CharField(
        max_length=100, 
        verbose_name="Часы работы",
        help_text="Пример: Пн-Пт 10:00-22:00, Сб-Вс 12:00-23:00"
    )
    rating = models.FloatField(default=4.5, verbose_name="Рейтинг")
    is_active = models.BooleanField(default=True, verbose_name="Активен")

    # Изображение
    logo = models.ImageField(
        upload_to='restaurant_logos/',
        blank=True,
        null=True,
        verbose_name="Логотип"
    )
    facade_image = models.ImageField(upload_to='restaurant_facades/', blank=True, null=True, verbose_name="Фото фасада")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Ресторан"
        verbose_name_plural = "Рестораны"

class Table(models.Model):
    number = models.IntegerField(unique=True, verbose_name="Номер столика")
    capacity = models.IntegerField(verbose_name="Вместимость")
    description = models.CharField(max_length=255, blank=True, verbose_name="Описание")
    is_active = models.BooleanField(default=True, verbose_name="Активный")
    
    def __str__(self):
        return f"Столик {self.number} ({self.capacity} чел.)"


class Reservation(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Ожидание подтверждения'),
        ('confirmed', 'Подтверждено'),
        ('cancelled', 'Отменено'),
        ('completed', 'Завершено'),
    )
    
    client_name = models.CharField(max_length=100, verbose_name="Имя клиента")
    client_phone = models.CharField(max_length=20, verbose_name="Телефон клиента")
    client_email = models.EmailField(blank=True, verbose_name="Email клиента")
    table = models.ForeignKey(Table, on_delete=models.CASCADE, verbose_name="Столик")
    date = models.DateField(verbose_name="Дата бронирования")
    time = models.TimeField(verbose_name="Время бронирования")
    guests_count = models.IntegerField(
        verbose_name="Количество гостей",
        validators=[MinValueValidator(1), MaxValueValidator(20)]
    )
    special_requests = models.TextField(blank=True, verbose_name="Особые пожелания")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Статус")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    
    class Meta:
        unique_together = ('table', 'date', 'time')
    
    def __str__(self):
        return f"{self.client_name} - {self.date} {self.time}"

