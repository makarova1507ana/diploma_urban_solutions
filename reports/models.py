from django.db import models

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.conf import settings

class Topic(models.Model):
    title = models.CharField(
        max_length=100,
        blank=False,  # Поле не может быть пустым
        error_messages={
            'blank': 'Поле не может быть пустым.'
        },
        default="Тема 1"
    )
    description = models.TextField(blank=True, null=True)

    def clean(self):
        # Удаление пробелов в начале и в конце для title
        self.title = self.title.strip()
        # Проверка на минимальную длину
        if len(self.title) < 1:
            raise ValidationError({'title': 'Заголовок должен содержать хотя бы 1 символ.'})

    def __str__(self):
        return self.title


class Report(models.Model):
    # Внешний ключ на пользователя (создателя проблемы)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        db_column='user_id',
        related_name='reports'
    )
    # Внешний ключ на категорию
    category = models.ForeignKey(
        'Topic',
        on_delete=models.CASCADE,
        db_column='topic_id',
        related_name='reports'
    )
    title = models.CharField(max_length=255)

    # Описание проблемы (необязательное, до 350 символов)
    description = models.TextField(blank=True, null=True, max_length=350)

    # Категория в текстовом формате (если нужно)
    category_text = models.CharField(max_length=100, blank=True, null=True, db_column='category')

    # Координаты места происшествия
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    # Поле для текстового адреса
    address = models.TextField(blank=True, null=True)

    # Поле для хранения URL изображения (если потребуется)
    image_url = models.TextField(blank=True, null=True)

    # Местоположение в текстовом формате
    location = models.TextField(blank=True, null=True)

    # Поле статуса с возможными значениями
    STATUS_CHOICES = [
        ('new', 'Новая'),
        ('in_progress', 'В обработке'),
        ('resolved', 'Решена'),
        ('rejected', 'Отклонена')
    ]
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='new',
        blank=True,
        null=True
    )

    # Время создания и обновления
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'reports'

    def __str__(self):
        return self.title


# Модель для изображений, привязанных к отчету
class ReportImage(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="reports/")

    def __str__(self):
        return f"Image for report {self.report.id}"


class ModerationLog(models.Model):
    problem = models.ForeignKey(
        Report,
        on_delete=models.CASCADE,
        db_column='problem_id',
        related_name='moderation_logs'
    )
    moderator = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Используем кастомную модель пользователя
        on_delete=models.CASCADE,
        db_column='moderator_id',
        related_name='moderation_logs'
    )
    action = models.CharField(max_length=50, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'moderation_logs'

    def __str__(self):
        return f"{self.moderator.email} - {self.action}"


class Notification(models.Model):
    problem = models.ForeignKey(
        Report,
        on_delete=models.CASCADE,
        db_column='problem_id',
        related_name='notifications'
    )
    recipient_email = models.EmailField(max_length=255)
    sent_at = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        db_table = 'notifications'

    def __str__(self):
        return f"Notification to {self.recipient_email}"
