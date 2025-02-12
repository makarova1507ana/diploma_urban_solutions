from django.contrib.auth.models import AbstractUser
from django.db import models

# Кастомная модель пользователя на основе AbstractUser
class User(AbstractUser):
    username = None  # убираем поле username
    email = models.EmailField('email address', unique=True)
    role = models.CharField(max_length=50, blank=True, null=True)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    district = models.CharField(max_length=100, blank=True, null=True)
    preferred_contact = models.CharField(
        "Предпочитаемый способ связи",
        max_length=20,
        choices=[
            ('email', 'Email'),
            ('phone', 'Телефон'),
            ('sms', 'СМС'),
        ],
        default='email',
        blank=True,
        null=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # дополнительные обязательные поля можно указать здесь

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.email
