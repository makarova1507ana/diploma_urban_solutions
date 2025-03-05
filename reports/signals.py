# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Report

@receiver(post_save, sender=Report)
def send_status_change_notification(sender, instance, created, **kwargs):
    """Отправка уведомления при изменении статуса заявки"""
    if not created:
        try:
            old_report = Report.objects.get(pk=instance.pk)
            if old_report.status != instance.status:
                instance.send_status_change_email()
        except Report.DoesNotExist:
            pass
