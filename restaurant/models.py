from django.db import models

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


class Reservation(models.Model):
    # Связь с рестораном
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, verbose_name="Ресторан")
    
    # Основные данные
    name = models.CharField(max_length=100, verbose_name="Имя клиента")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    
    # Детали бронирования
    date_time = models.DateTimeField(verbose_name="Дата и время")
    guests = models.PositiveIntegerField(default=1, verbose_name="Количество гостей")
    special_requests = models.TextField(blank=True, verbose_name="Особые пожелания")
    
    # Статус
    STATUS_CHOICES = [
        ('pending', 'В ожидании'),
        ('confirmed', 'Подтверждено'),
        ('cancelled', 'Отменено'),
    ]
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Статус"
    )
    
    def __str__(self):
        return f"{self.name} - {self.restaurant.name} ({self.date_time.strftime('%d.%m.%Y %H:%M')})"
    
    class Meta:
        verbose_name = "Бронирование"
        verbose_name_plural = "Бронирования"
        ordering = ['-date_time']  # Сортировка по дате (сначала новые)