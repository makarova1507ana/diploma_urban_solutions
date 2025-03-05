import datetime

from django.contrib import admin
from .models import Report, Topic, Service, ReportImage, Comment, CommentImage, ModerationLog
from django.contrib.admin import DateFieldListFilter
from django.utils.html import format_html
from django.urls import reverse


# Модель для Topic
@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'description')
    search_fields = ('title',)

# Модель для Service
@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_email')
    search_fields = ('name', 'contact_email')

# Модель для Report
@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'category', 'status', 'created_at', 'updated_at', 'responsible_service', 'download_report')
    search_fields = ('title', 'user__username', 'category__title', 'status')
    list_filter = (
        'status',
        'category',
        'responsible_service',
        ('created_at', DateFieldListFilter),  # Фильтрация по дате создания
        ('updated_at', DateFieldListFilter),  # Фильтрация по дате обновления
    )

    def download_report(self, obj):
        # Формируем ссылку для скачивания PDF
        url = reverse('generate_report_pdf', kwargs={'report_id': obj.id})
        return format_html('<a href="{}" target="_blank">Скачать отчет в PDF</a>', url)

    download_report.short_description = "Отчет"

# Модель для ReportImage
@admin.register(ReportImage)
class ReportImageAdmin(admin.ModelAdmin):
    list_display = ('report', 'image')
    search_fields = ('report__title',)

# Модель для Comment
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('report', 'user', 'created_at')
    search_fields = ('user__username', 'report__title')
    list_filter = ('created_at',)

# Модель для CommentImage
@admin.register(CommentImage)
class CommentImageAdmin(admin.ModelAdmin):
    list_display = ('comment', 'image', 'image_name')
    search_fields = ('comment__report__title', 'image_name')

# Модель для ModerationLog
@admin.register(ModerationLog)
class ModerationLogAdmin(admin.ModelAdmin):
    list_display = ('problem', 'moderator', 'action', 'created_at')
    search_fields = ('problem__title', 'moderator__email', 'action')
    list_filter = ('action', 'created_at')


