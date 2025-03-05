from django.apps import AppConfig


class ProblemsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reports'
    verbose_name = "Отчеты о проблемах"



class ReportsConfig(AppConfig):
    name = 'reports'

    def ready(self):
        import reports.signals
