# Generated by Django 5.1.6 on 2025-02-11 20:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='preferred_contact',
            field=models.CharField(blank=True, choices=[('email', 'Email'), ('phone', 'Телефон'), ('sms', 'СМС')], default='email', max_length=20, null=True, verbose_name='Предпочитаемый способ связи'),
        ),
    ]
