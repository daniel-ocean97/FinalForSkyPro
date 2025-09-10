from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    username = None
    first_name = models.CharField(max_length=55, verbose_name="Имя")
    last_name = models.CharField(max_length=55, blank=True, null=True, verbose_name="Фамилия")
    email = models.EmailField(unique=True, verbose_name="Почта")
    phone_number = models.CharField(max_length=15, blank=True, null=True, verbose_name="Телефон")
    country = models.CharField(max_length=35, blank=True, null=True, verbose_name="Страна")
    avatar = models.ImageField(
        verbose_name="Аватар", null=True, blank=True, upload_to="users_avatar/"
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"