from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.urls import reverse
from users.models import User
from django.core.mail import EmailMessage
from datetime import timedelta
from django.db.models import Count

class Topic(models.Model):
    title = models.CharField(
        max_length=100,
        blank=False,
        error_messages={
            'blank': 'Поле не может быть пустым.'
        },
        default="Тема 1",
        verbose_name="Заголовок темы"
    )
    description = models.TextField(blank=True, null=True, verbose_name="Описание темы")

    def clean(self):
        # Удаление пробелов в начале и в конце для title
        self.title = self.title.strip()
        # Проверка на минимальную длину
        if len(self.title) < 1:
            raise ValidationError({'title': 'Заголовок должен содержать хотя бы 1 символ.'})

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Тема"
        verbose_name_plural = "Темы"


class Service(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название службы")
    contact_email = models.EmailField(verbose_name="Контактный email")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Служба"
        verbose_name_plural = "Службы"


class Report(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        db_column='user_id',
        related_name='reports',
        verbose_name="Пользователь"
    )
    category = models.ForeignKey(
        'Topic',
        on_delete=models.CASCADE,
        db_column='topic_id',
        related_name='reports',
        verbose_name="Категория"
    )
    title = models.CharField(max_length=255, verbose_name="Заголовок отчета")

    description = models.TextField(blank=True, null=True, max_length=350, verbose_name="Описание проблемы")

    latitude = models.FloatField(blank=True, null=True, verbose_name="Широта")
    longitude = models.FloatField(blank=True, null=True, verbose_name="Долгота")

    address = models.TextField(blank=True, null=True, verbose_name="Адрес")

    STATUS_CHOICES = [
        ('in_moderation', 'На модерации'),
        ('approved', 'Одобрена'),
        ('in_progress', 'В работе'),
        ('resolved', 'Решена'),
        ('rejected', 'Отклонена')
    ]

    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='in_moderation',
        blank=True,
        null=True,
        verbose_name="Статус"
    )

    responsible_service = models.ForeignKey(
        Service,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reports',
        db_column='service_id',
        verbose_name="Ответственная служба"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Время обновления")

    class Meta:
        db_table = 'reports'
        verbose_name = "Отчет о проблеме"
        verbose_name_plural = "Отчеты о проблемах"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('report_detail', kwargs={'pk': self.pk})

    def send_status_change_email(self):
        subject = f"Изменение статуса заявки: {self.title}"
        message = f"""
                    <html>
                    <head>
                        <style>
                            body {{
                                font-family: Arial, sans-serif;
                                background-color: #f4f4f9;
                                color: #333;
                                padding: 20px;
                            }}
                            .message-container {{
                                background-color: #ffffff;
                                border-radius: 8px;
                                padding: 20px;
                                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                            }}
                            .header {{
                                font-size: 20px;
                                color: #4CAF50;
                                font-weight: bold;
                            }}
                            .content {{
                                font-size: 16px;
                                color: #555;
                                margin-top: 10px;
                            }}
                        </style>
                    </head>
                    <body>
                        <div class="message-container">
                            <div class="header">Изменение статуса заявки</div>
                            <div class="content">
                                Статус вашей заявки <strong>'{self.title}'</strong> был изменен на: <strong>{self.get_status_display()}</strong>.
                            </div>
                        </div>
                    </body>
                    </html>
                    """

        recipient_email = self.user.email

        # Создаем объект EmailMessage и указываем, что письмо в формате HTML
        email = EmailMessage(
            subject=subject,
            body=message,
            from_email=settings.EMAIL_HOST_USER,
            to=[recipient_email],
        )
        email.content_subtype = 'html'  # Устанавливаем MIME-тип как HTML
        email.send(fail_silently=False)

    def save(self, *args, **kwargs):
        # Если статус изменился, отправляем уведомление
        if self.pk:
            old_status = Report.objects.get(pk=self.pk).status
            if old_status != self.status:
                self.send_status_change_email()

        super().save(*args, **kwargs)


class ReportImage(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name="images", verbose_name="Отчет")
    image = models.ImageField(upload_to="reports/", verbose_name="Изображение")

    def __str__(self):
        return f"Изображение для отчета {self.report.id}"

    def clean(self):
        if self.report.images.count() >= 5:
            raise ValidationError("Нельзя загружать больше 5 изображений для одного отчета.")

    def save(self, *args, **kwargs):
        self.full_clean()  # Вызывает clean перед сохранением
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Изображение отчета"
        verbose_name_plural = "Изображения отчетов"


class Comment(models.Model):
    report = models.ForeignKey(Report, related_name='comments', on_delete=models.CASCADE, verbose_name="Отчет")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    text = models.TextField(verbose_name="Текст комментария")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return f"Комментарий от {self.user.username} на {self.report.title}"

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"


class CommentImage(models.Model):
    comment = models.ForeignKey(Comment, related_name="images", on_delete=models.CASCADE, verbose_name="Комментарий")
    image = models.ImageField(upload_to="comments/", verbose_name="Изображение")
    image_name = models.CharField(max_length=255, unique=True, default=None, verbose_name="Имя изображения")

    def __str__(self):
        return f"Изображение для комментария {self.comment.id}"

    class Meta:
        verbose_name = "Изображение комментария"
        verbose_name_plural = "Изображения комментариев"


class ModerationLog(models.Model):
    problem = models.ForeignKey(
        Report,
        on_delete=models.CASCADE,
        db_column='problem_id',
        related_name='moderation_logs',
        verbose_name="Отчет о проблеме"
    )
    moderator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        db_column='moderator_id',
        related_name='moderation_logs',
        verbose_name="Модератор"
    )
    action = models.CharField(max_length=50, blank=True, null=True, verbose_name="Действие")
    comment = models.TextField(blank=True, null=True, verbose_name="Комментарий")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        db_table = 'moderation_logs'
        verbose_name = "Журнал модерации"
        verbose_name_plural = "Журналы модерации"

    def __str__(self):
        return f"{self.moderator.email} - {self.action}"



