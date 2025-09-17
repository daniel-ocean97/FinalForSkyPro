from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.text import slugify


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
        help_text="Пример: Пн-Пт 10:00-22:00, Сб-Вс 12:00-23:00",
    )
    rating = models.FloatField(default=4.5, verbose_name="Рейтинг")
    is_active = models.BooleanField(default=True, verbose_name="Активен")

    # Изображение
    logo = models.ImageField(
        upload_to="restaurant_logos/", blank=True, null=True, verbose_name="Логотип"
    )
    facade_image = models.ImageField(
        upload_to="restaurant_facades/",
        blank=True,
        null=True,
        verbose_name="Фото фасада",
    )

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

    def is_available(self, date, time):
        """Проверяет, свободен ли столик в указанные дату и время"""

        # Преобразуем время в объект datetime для сравнения
        datetime_selected = timezone.make_aware(timezone.datetime.combine(date, time))

        # Проверяем бронирования на этот столик в выбранное время ±2 часа
        reservations = Reservation.objects.filter(
            table=self, date=date, status__in=["pending", "confirmed"]
        ).exclude(status="cancelled")

        for reservation in reservations:
            reservation_time = timezone.make_aware(
                timezone.datetime.combine(reservation.date, reservation.time)
            )
            time_diff = abs((reservation_time - datetime_selected).total_seconds())

            # Если время бронирования пересекается с выбранным временем
            if time_diff < 7200:  # 2 часа
                print(f"Table {self.number} is NOT available")
                return False

        return True

    def __str__(self):
        return f"Столик {self.number} ({self.capacity} чел.)"


class Reservation(models.Model):
    STATUS_CHOICES = (
        ("pending", "Ожидание подтверждения"),
        ("confirmed", "Подтверждено"),
        ("cancelled", "Отменено"),
        ("completed", "Завершено"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reservations",
        verbose_name="Пользователь",
    )
    client_name = models.CharField(max_length=100, verbose_name="Имя клиента")
    client_phone = models.CharField(max_length=20, verbose_name="Телефон клиента")
    client_email = models.EmailField(blank=True, verbose_name="Email клиента")
    table = models.ForeignKey(Table, on_delete=models.CASCADE, verbose_name="Столик")
    date = models.DateField(verbose_name="Дата бронирования")
    time = models.TimeField(verbose_name="Время бронирования")
    guests_count = models.IntegerField(
        verbose_name="Количество гостей",
        validators=[MinValueValidator(1), MaxValueValidator(20)],
    )
    special_requests = models.TextField(blank=True, verbose_name="Особые пожелания")
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="pending", verbose_name="Статус"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")

    class Meta:
        unique_together = ("table", "date", "time")

    def __str__(self):
        return f"{self.client_name} - {self.date} {self.time}"


class Feedback(models.Model):
    name = models.CharField(max_length=150, verbose_name="Имя")
    phone = models.CharField(max_length=150)
    email = models.CharField(max_length=150)
    subject = models.CharField(max_length=150)
    message = models.CharField(max_length=150)

    def __str__(self):
        return f"Обращение {self.name} по теме {self.subject}"


class DishCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название категории")
    slug = models.SlugField(unique=True, verbose_name="Слаг")
    description = models.TextField(blank=True, verbose_name="Описание")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок отображения")
    is_visible = models.BooleanField(default=True, verbose_name="Отображать на сайте")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория блюд"
        verbose_name_plural = "Категории блюд"
        ordering = ["order"]


class Dish(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название блюда")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="Slug")
    category = models.ForeignKey(DishCategory, on_delete=models.CASCADE, related_name="dishes", verbose_name="Категория")
    description = models.TextField(verbose_name="Описание")
    ingredients = models.CharField(max_length=255, blank=True, verbose_name="Ингредиенты")
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Цена")
    image = models.ImageField(upload_to='dishes/', blank=True, null=True, verbose_name="Изображение")
    is_available = models.BooleanField(default=True, verbose_name="Доступно")
    is_special = models.BooleanField(default=False, verbose_name="Специальное предложение")
    is_vegetarian = models.BooleanField(default=False, verbose_name="Вегетарианское")
    is_spicy = models.BooleanField(default=False, verbose_name="Острое")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Блюдо"
        verbose_name_plural = "Блюда"
        ordering = ["category", "name"]
