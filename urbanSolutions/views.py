from django.views.generic.base import TemplateView
from reports.models import Report, Topic
import random
from collections import Counter
from users.models import User
from django.utils.timezone import now
from datetime import timedelta
from django.db.models import Count, Avg, F, ExpressionWrapper, fields
from django.db.models.functions import TruncMonth


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


class About(TemplateView):
    template_name = 'about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        last_7_days = now() - timedelta(days=7)
        last_year = now() - timedelta(days=365)

        # Данные за последние 7 дней
        last_7_days_reports = Report.objects.filter(created_at__gte=last_7_days).count()
        last_7_days_updates = Report.objects.filter(updated_at__gte=last_7_days).count()
        last_7_days_resolved = Report.objects.filter(
            status='resolved', updated_at__gte=last_7_days
        ).count()

        # Топ-5 категорий за последние 7 дней
        category_counts = (
            Report.objects.filter(created_at__gte=last_7_days)
            .values('category__title')
            .annotate(count=Count('id'))
            .order_by('-count')[:5]
        )

        reported_in_top_categories = sum(cat['count'] for cat in category_counts)
        other_categories_count = last_7_days_reports - reported_in_top_categories

        # Данные по месяцам за последний год (с использованием TruncMonth для SQLite)
        reports_per_month = (
            Report.objects.filter(created_at__gte=last_year)
            .annotate(month=TruncMonth('created_at'))
            .values('month')
            .annotate(count=Count('id'))
            .order_by('month')
        )

        months = []
        report_counts = []
        for entry in reports_per_month:
            # entry["month"] – это дата, округленная до начала месяца
            months.append(entry["month"].strftime("%Y-%m"))  # Пример: '2024-02'
            report_counts.append(entry["count"])

        # Расчет среднего времени решения (в часах)
        resolved_reports = Report.objects.filter(status='resolved', updated_at__isnull=False)
        avg_resolution_time = resolved_reports.annotate(
            resolution_time=ExpressionWrapper(
                F('updated_at') - F('created_at'),
                output_field=fields.DurationField()
            )
        ).aggregate(avg_time=Avg('resolution_time'))['avg_time']

        # Преобразуем в часы
        avg_resolution_hours = round(avg_resolution_time.total_seconds() / 3600, 2) if avg_resolution_time else "Нет данных"

        # Передача данных в шаблон
        context.update({
            'last_7_days_reports': last_7_days_reports,
            'last_7_days_updates': last_7_days_updates,
            'last_7_days_resolved': last_7_days_resolved,
            'top_categories': category_counts,
            'other_categories_count': other_categories_count,
            'months': months,
            'report_counts': report_counts,
            'avg_resolution_hours': avg_resolution_hours
        })
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


from django.http import HttpResponse
from django.http import HttpResponse
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def generate_report_pdf(request, report_id):
    # Получаем отчет по ID
    report = Report.objects.get(id=report_id)

    # Подготовка данных для PDF
    data = [
        ['Категория', 'Статус', 'Описание'],
    ]

    # Заполнение данных для отчета
    data.append([report.category.title, report.get_status_display(), report.description])

    # Создаем PDF
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)

    # Регистрируем шрифт с поддержкой кириллицы
    pdfmetrics.registerFont(TTFont('FreeSerif', '/path/to/your/FreeSerif.ttf'))  # Замените на путь к файлу шрифта
    pdf.setFont("FreeSerif", 10)

    # Добавляем заголовок
    pdf.drawString(100, 750, "Отчет о проблеме")

    # Добавляем данные таблицы
    y_position = 700
    for row in data:
        pdf.drawString(100, y_position, row[0])  # Категория
        pdf.drawString(250, y_position, row[1])  # Статус
        pdf.drawString(400, y_position, row[2])  # Описание
        y_position -= 20  # Сдвиг вниз для следующей строки

    # Закрываем PDF и возвращаем его как ответ
    pdf.showPage()
    pdf.save()

    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')
