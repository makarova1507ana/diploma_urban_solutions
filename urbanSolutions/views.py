from django.views.generic.base import TemplateView
from reports.models import Report, Topic
import random
from collections import Counter

from users.models import User


class Index(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Получаем все решённые проблемы
        resolved_reports = list(Report.objects.filter(status='resolved'))  # Преобразуем в список

        # Получаем количество решённых проблем
        resolved_reports_count = len(resolved_reports)

        # Получаем список всех категорий (тем)
        topics = [report.category for report in resolved_reports]

        # Находим самую часто встречающуюся категорию (тему)
        topic_counts = Counter(topics)
        most_common_topic = topic_counts.most_common(1)  # Получаем наиболее встречающуюся категорию

        if most_common_topic:
            most_common_topic = most_common_topic[0][0]
            # Выбираем случайную проблему из самой популярной категории
            reports_in_topic = [report for report in resolved_reports if report.category == most_common_topic]
            random_report = random.choice(reports_in_topic) if reports_in_topic else None
        else:
            random_report = None



        # Получаем количество зарегистрированных пользователей
        users_count = User.objects.count()

        # Передаем данные в контекст
        context["resolved_reports_count"] = resolved_reports_count
        context["users_count"] = users_count
        context["reports"] = random.sample(resolved_reports, min(3, len(resolved_reports)))  # случайные три
        context["most_common_topic"] = most_common_topic
        context["random_report"] = random_report

        return context


class ErrorView(TemplateView):
    template_name = 'errors.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Передаем статус-код в шаблон
        context['status_code'] = kwargs.get('status_code', 500)

        # Генерируем сообщение об ошибке
        status_code = context['status_code']
        if 400 <= status_code < 500:
            context['error_message'] = 'Ошибка клиента. Проверьте ваш запрос.'
        elif 500 <= status_code < 600:
            context['error_message'] = 'Ошибка сервера. Пожалуйста, попробуйте позже.'
        else:
            context['error_message'] = 'Неизвестная ошибка.'
        return context