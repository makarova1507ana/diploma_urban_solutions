from django.contrib import admin
from .models import User  # Импортируем вашу модель пользователя


class UserAdmin(admin.ModelAdmin):
    # Настройки отображения полей в админке
    list_display = (
    'email', 'full_name', 'role', 'phone_number', 'district', 'preferred_contact', 'is_active', 'date_joined')
    search_fields = ('email', 'username', 'full_name')  # Добавляем возможность поиска по этим полям
    list_filter = ('role', 'preferred_contact', 'is_active')  # Фильтры по этим полям
    ordering = ('date_joined',)  # Сортировка по дате добавления

    # Настройки для редактирования
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('full_name', 'phone_number', 'address', 'district')}),
        ('Permissions', {'fields': ('role', 'is_active')}),
        ('Contact preferences', {'fields': ('preferred_contact',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
            'email', 'username', 'full_name', 'role', 'phone_number', 'address', 'district', 'preferred_contact',
            'password1', 'password2'),
        }),
    )


# Регистрируем модель с кастомным классом администратора
admin.site.register(User, UserAdmin)
