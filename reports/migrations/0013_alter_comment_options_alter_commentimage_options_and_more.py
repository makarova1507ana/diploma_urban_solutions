# Generated by Django 5.1.6 on 2025-03-05 21:53

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0012_service_report_responsible_service'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={'verbose_name': 'Комментарий', 'verbose_name_plural': 'Комментарии'},
        ),
        migrations.AlterModelOptions(
            name='commentimage',
            options={'verbose_name': 'Изображение комментария', 'verbose_name_plural': 'Изображения комментариев'},
        ),
        migrations.AlterModelOptions(
            name='moderationlog',
            options={'verbose_name': 'Журнал модерации', 'verbose_name_plural': 'Журналы модерации'},
        ),
        migrations.AlterModelOptions(
            name='notification',
            options={'verbose_name': 'Уведомление', 'verbose_name_plural': 'Уведомления'},
        ),
        migrations.AlterModelOptions(
            name='report',
            options={'verbose_name': 'Отчет о проблеме', 'verbose_name_plural': 'Отчеты о проблемах'},
        ),
        migrations.AlterModelOptions(
            name='reportimage',
            options={'verbose_name': 'Изображение отчета', 'verbose_name_plural': 'Изображения отчетов'},
        ),
        migrations.AlterModelOptions(
            name='service',
            options={'verbose_name': 'Служба', 'verbose_name_plural': 'Службы'},
        ),
        migrations.AlterModelOptions(
            name='topic',
            options={'verbose_name': 'Тема', 'verbose_name_plural': 'Темы'},
        ),
        migrations.AlterField(
            model_name='comment',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата создания'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='report',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='reports.report', verbose_name='Отчет'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='text',
            field=models.TextField(verbose_name='Текст комментария'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
        migrations.AlterField(
            model_name='commentimage',
            name='comment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='reports.comment', verbose_name='Комментарий'),
        ),
        migrations.AlterField(
            model_name='commentimage',
            name='image',
            field=models.ImageField(upload_to='comments/', verbose_name='Изображение'),
        ),
        migrations.AlterField(
            model_name='commentimage',
            name='image_name',
            field=models.CharField(default=None, max_length=255, unique=True, verbose_name='Имя изображения'),
        ),
        migrations.AlterField(
            model_name='moderationlog',
            name='action',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Действие'),
        ),
        migrations.AlterField(
            model_name='moderationlog',
            name='comment',
            field=models.TextField(blank=True, null=True, verbose_name='Комментарий'),
        ),
        migrations.AlterField(
            model_name='moderationlog',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата создания'),
        ),
        migrations.AlterField(
            model_name='moderationlog',
            name='moderator',
            field=models.ForeignKey(db_column='moderator_id', on_delete=django.db.models.deletion.CASCADE, related_name='moderation_logs', to=settings.AUTH_USER_MODEL, verbose_name='Модератор'),
        ),
        migrations.AlterField(
            model_name='moderationlog',
            name='problem',
            field=models.ForeignKey(db_column='problem_id', on_delete=django.db.models.deletion.CASCADE, related_name='moderation_logs', to='reports.report', verbose_name='Отчет о проблеме'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='problem',
            field=models.ForeignKey(db_column='problem_id', on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='reports.report', verbose_name='Отчет о проблеме'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='recipient_email',
            field=models.EmailField(max_length=255, verbose_name='Email получателя'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='sent_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Дата отправки'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='status',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Статус'),
        ),
        migrations.AlterField(
            model_name='report',
            name='address',
            field=models.TextField(blank=True, null=True, verbose_name='Адрес'),
        ),
        migrations.AlterField(
            model_name='report',
            name='category',
            field=models.ForeignKey(db_column='topic_id', on_delete=django.db.models.deletion.CASCADE, related_name='reports', to='reports.topic', verbose_name='Категория'),
        ),
        migrations.AlterField(
            model_name='report',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Время создания'),
        ),
        migrations.AlterField(
            model_name='report',
            name='description',
            field=models.TextField(blank=True, max_length=350, null=True, verbose_name='Описание проблемы'),
        ),
        migrations.AlterField(
            model_name='report',
            name='latitude',
            field=models.FloatField(blank=True, null=True, verbose_name='Широта'),
        ),
        migrations.AlterField(
            model_name='report',
            name='longitude',
            field=models.FloatField(blank=True, null=True, verbose_name='Долгота'),
        ),
        migrations.AlterField(
            model_name='report',
            name='responsible_service',
            field=models.ForeignKey(blank=True, db_column='service_id', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reports', to='reports.service', verbose_name='Ответственная служба'),
        ),
        migrations.AlterField(
            model_name='report',
            name='status',
            field=models.CharField(blank=True, choices=[('in_moderation', 'На модерации'), ('new', 'Новая'), ('in_progress', 'В обработке'), ('resolved', 'Решена'), ('rejected', 'Отклонена')], default='in_moderation', max_length=50, null=True, verbose_name='Статус'),
        ),
        migrations.AlterField(
            model_name='report',
            name='title',
            field=models.CharField(max_length=255, verbose_name='Заголовок отчета'),
        ),
        migrations.AlterField(
            model_name='report',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Время обновления'),
        ),
        migrations.AlterField(
            model_name='report',
            name='user',
            field=models.ForeignKey(db_column='user_id', on_delete=django.db.models.deletion.CASCADE, related_name='reports', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
        migrations.AlterField(
            model_name='reportimage',
            name='image',
            field=models.ImageField(upload_to='reports/', verbose_name='Изображение'),
        ),
        migrations.AlterField(
            model_name='reportimage',
            name='report',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='reports.report', verbose_name='Отчет'),
        ),
        migrations.AlterField(
            model_name='service',
            name='contact_email',
            field=models.EmailField(max_length=254, verbose_name='Контактный email'),
        ),
        migrations.AlterField(
            model_name='service',
            name='name',
            field=models.CharField(max_length=255, verbose_name='Название службы'),
        ),
        migrations.AlterField(
            model_name='topic',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='Описание темы'),
        ),
        migrations.AlterField(
            model_name='topic',
            name='title',
            field=models.CharField(default='Тема 1', error_messages={'blank': 'Поле не может быть пустым.'}, max_length=100, verbose_name='Заголовок темы'),
        ),
    ]
