from django.db import models

from django.conf import settings



class Category(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        db_table = 'categories'

    def __str__(self):
        return self.name


class Problem(models.Model):
    # Внешний ключ на пользователя (создателя проблемы)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Используем кастомную модель пользователя
        on_delete=models.CASCADE,
        db_column='user_id',
        related_name='problems'
    )
    # Внешний ключ на категорию
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        db_column='category_id',
        related_name='problems'
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    # Дополнительное текстовое поле, сопоставленное со столбцом "category" в БД
    category_text = models.CharField(max_length=100, blank=True, null=True, db_column='category')
    image_url = models.TextField(blank=True, null=True)
    location = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'problems'

    def __str__(self):
        return self.title


class ModerationLog(models.Model):
    problem = models.ForeignKey(
        Problem,
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
        Problem,
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
