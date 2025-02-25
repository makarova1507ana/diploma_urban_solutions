from django.contrib import admin
from .models import Topic, Report, ReportImage

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'description')  # Поля, которые будут отображаться в списке
    search_fields = ('title',)  # Поиск по заголовку
    list_filter = ('title',)  # Фильтрация по заголовку

# Inline для отображения изображений в форме отчета
class ReportImageInline(admin.TabularInline):  # Можно использовать StackedInline для вертикального отображения
    model = ReportImage
    extra = 1  # Количество пустых форм для добавления новых изображений
    readonly_fields = ('image',)  # Сделать поле изображения доступным только для чтения (если нужно)

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'category', 'status', 'created_at', 'updated_at')  # Поля в списке
    list_filter = ('status', 'category', 'created_at')  # Фильтрация по статусу, категории и времени
    search_fields = ('title', 'description', 'category__title')  # Поиск по полям
    inlines = [ReportImageInline]  # Включаем возможность добавления изображений для отчета

@admin.register(ReportImage)
class ReportImageAdmin(admin.ModelAdmin):
    list_display = ('report', 'image')  # Поля в списке
    search_fields = ('report__title',)  # Поиск по заголовку отчета
    list_filter = ('report',)  # Фильтрация по отчету

