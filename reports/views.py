import os

from django.views.generic import TemplateView, DetailView, ListView
from django.shortcuts import redirect, render
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from time import sleep
from django.db.models import Q
from django.http import JsonResponse

from .models import ReportImage, Topic, CommentImage

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from .models import Report
from .forms import CommentForm, ReportForm
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from geopy.exc import GeocoderTimedOut
from django.core.files.uploadedfile import InMemoryUploadedFile

# Представление для добавления комментария к отчету. Требуется, чтобы пользователь был авторизован.
@method_decorator(login_required, name='dispatch')
class AddCommentView(View):
    def get(self, request, report_id):
        """
        Отображение страницы с формой добавления комментария к отчету.
        """
        report = get_object_or_404(Report, id=report_id)  # Получаем отчет по ID
        form = CommentForm()  # Инициализируем пустую форму комментария
        return render(request, 'report.html', {'report': report, 'form': form})

    def post(self, request, report_id):
        """
        Обработка POST-запроса для добавления комментария.
        Сохраняет комментарий и изображения, если они были загружены.
        """
        report = get_object_or_404(Report, id=report_id)  # Получаем отчет по ID
        form = CommentForm(request.POST, request.FILES)  # Получаем форму с данными

        if form.is_valid():
            # Создаем новый комментарий и связываем его с отчетом и пользователем
            comment = form.save(report=report, user=request.user)

            # Если есть изображения, сохраняем их
            if 'images' in request.FILES:
                for image in request.FILES.getlist('images'):
                    CommentImage.objects.create(comment=comment, image=image)

            # Перенаправляем на страницу отчета
            return redirect('reports:report_detail', pk=report.id)

        # В случае ошибки рендерим форму с ошибками
        return render(request, 'report.html', {'report': report, 'form': form, 'errors': form.errors})

# Страница с перечнем всех доступных тем
class TopicsPage(TemplateView):
    template_name = 'topics.html'

    def get_context_data(self, **kwargs):
        """
        Добавление всех тем в контекст для отображения на странице.
        """
        topics = Topic.objects.all()  # Получаем все темы из базы данных
        context = super().get_context_data(**kwargs)  # Получаем базовый контекст
        context['topics'] = topics  # Добавляем темы в контекст
        return context

# Страница с подробной информацией по конкретной теме
class TopicDetailView(DetailView):
    model = Topic
    template_name = 'topic_detail.html'
    context_object_name = 'topic'

    def get_context_data(self, **kwargs):
        """
        Добавление связанных отчетов к теме. Выбираются случайные 3 отчетов.
        """
        context = super().get_context_data(**kwargs)
        topic = context['topic']
        # Фильтрация отчётов со статусом "на модерации":
        moderation_status = 'in_moderation'
        queryset = Report.objects.filter(category=topic).order_by('?')


        queryset = queryset.exclude(status=moderation_status)
        related_reports = queryset[:3]  # Получаем 3 случайных отчета
        context['related_reports'] = related_reports  # Добавляем связанные отчеты в контекст
        return context

# Страница с подробной информацией о конкретном отчете
class ReportDetailView(DetailView):
    model = Report
    template_name = 'report.html'
    context_object_name = 'report'

    def get_context_data(self, **kwargs):
        # Получаем контекст по умолчанию
        context = super().get_context_data(**kwargs)

        # Получаем все изображения, связанные с отчетом
        report_images = ReportImage.objects.filter(report=self.object)
        # Добавляем изображения в контекст
        context['report_images'] = report_images
        return context

class ReportFilterMixin:
    """
    Миксин для фильтрации отчетов и формирования общих элементов контекста.
    """
    def get_filtered_reports(self):
        queryset = Report.objects.all()

        # Поиск по части текста в названии и описании
        search_query = self.request.GET.get('text')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) | Q(description__icontains=search_query)
            )

        # Фильтрация по статусу
        status = self.request.GET.get('status')
        if status:
            status_mapping = {
                'На модерации': 'in_moderation',
                'Новая': 'new',
                'В обработке': 'in_progress',
                'Решена': 'resolved',
                'Отклонена': 'rejected'
            }
            # Получаем значение для фильтрации из словаря, если его нет — оставляем оригинальное значение
            status_en = status_mapping.get(status, status)
            queryset = queryset.filter(status=status_en)

        # Фильтрация по категории
        category = self.request.GET.get('category')
        if category and category != "None":
            queryset = queryset.filter(category__title=category)

        # Фильтрация по временным диапазонам
        time_filter = self.request.GET.get('time_filter')
        if time_filter:
            today = timezone.now().date()
            if time_filter == 'last_day':
                queryset = queryset.filter(created_at__date=today)
            elif time_filter == 'last_week':
                start_of_week = today - timedelta(days=today.weekday())
                queryset = queryset.filter(created_at__date__gte=start_of_week)
            elif time_filter == 'last_month':
                start_of_month = today.replace(day=1)
                queryset = queryset.filter(created_at__date__gte=start_of_month)
            elif time_filter == 'last_year':
                start_of_year = today.replace(month=1, day=1)
                queryset = queryset.filter(created_at__date__gte=start_of_year)

        # Фильтр по "Мои отчёты"
        if self.request.GET.get('is_mine'):
            queryset = queryset.filter(user=self.request.user)

        # Фильтрация отчетов со статусом "на модерации":
        moderation_status = 'in_moderation'
        if self.request.user.is_authenticated:
            queryset = queryset.exclude(Q(status=moderation_status) & ~Q(user=self.request.user))
        else:
            queryset = queryset.exclude(status=moderation_status)

        return queryset

    def get_filter_context(self):
        """
        Формирует словарь с общими элементами контекста для фильтров.
        """
        return {
            'status_filter': self.request.GET.get('status'),
            'category_filter': self.request.GET.get('category'),
            'time_filter': self.request.GET.get('time_filter'),
            'is_mine': self.request.GET.get('is_mine'),
            'search_query': self.request.GET.get('text', ''),
            'statuses': Report.STATUS_CHOICES,
            'categories': Topic.objects.values_list('id', 'title'),
        }

# Представление с картой
class Map(ReportFilterMixin, TemplateView):
    template_name = 'map.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reports'] = self.get_filtered_reports()  # Передаем отфильтрованные отчеты
        context.update(self.get_filter_context())         # Добавляем общие элементы фильтра
        return context

# Представление с перечнем отчетов
class Reports(ReportFilterMixin, ListView):
    model = Report
    template_name = 'reports.html'
    context_object_name = 'reports'
    paginate_by = 10  # Количество отчетов на одной странице

    def get_queryset(self):
        # Возвращаем отфильтрованные отчеты, отсортированные по дате обновления (по убыванию)
        return self.get_filtered_reports().order_by('-updated_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_filter_context())
        return context

# Стартовая страница для этапа 1 добавления отчета
class Step1View(TemplateView):
    template_name = 'step1.html'

    def post(self, request, *args, **kwargs):
        """
        Обработка POST-запроса для сохранения координат в сессии и перехода ко второму этапу.
        """
        lat = request.POST.get('lat')
        lon = request.POST.get('lon')

        # Сохраняем координаты в сессии
        request.session['lat'] = lat
        request.session['lon'] = lon

        # Переадресация на второй этап
        return redirect('reports:step2')

    def get_context_data(self, **kwargs):
        """
        Добавление флага для скрытия кнопки отчета на странице.
        """
        context = super().get_context_data(**kwargs)
        context['hide_report_button'] = True  # Скрываем кнопку
        return context

# Страница с выбором темы для отчета
class Step2View(TemplateView):
    template_name = 'step2.html'

    def get_context_data(self, **kwargs):
        """
        Добавление списка доступных тем в контекст для отображения на странице.
        """
        context = super().get_context_data(**kwargs)
        context['hide_report_button'] = True  # Скрываем кнопку
        context['topics'] = Topic.objects.all()  # Передаем список тем

        return context

    def post(self, request, *args, **kwargs):
        """
        Сохранение выбранной темы и координат в сессии, переход к следующему этапу.
        """
        selected_topic = request.POST.get('selected_topic')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')

        # Сохраняем выбранную тему и координаты в сессии
        request.session['selected_topic'] = selected_topic
        request.session['latitude'] = latitude
        request.session['longitude'] = longitude

        # Переход к step3
        return redirect('reports:step3')

# Страница для третьего этапа добавления отчета с обратным геокодированием
class Step3View(TemplateView):
    template_name = "step3.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["hide_report_button"] = True
        upload_url = self.request.build_absolute_uri('reports:upload')  # Формируем абсолютный URL


        # Передаем данные в контекст
        form = ReportForm()
        context.update({
            "upload_url": upload_url,
            "form": form,  # Передаем форму в контекст
        })
        return context

    def reverse_geocode(self, latitude, longitude, retries=3):
        if not latitude or not longitude:
            return "Адрес не найден"

        geolocator = Nominatim(user_agent="geo_app")
        for attempt in range(retries):
            try:
                location = geolocator.reverse(f"{latitude}, {longitude}", exactly_one=True)
                if location and location.address:
                    return location.address
            except GeocoderTimedOut:
                sleep(2)
            except Exception as e:
                print(f"Ошибка геокодирования: {e}")
        return "Адрес не найден"

    def post(self, request, *args, **kwargs):

        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.user = request.user
            report.save()
            return JsonResponse({"status": "success", "report_id": report.id})
        else:
            errors = form.errors.as_json()
            return JsonResponse({"status": "error", "errors": errors}, status=400)

def images_upload(request):
    if request.method == "POST" and request.FILES.get("file"):
        file = request.FILES["file"]
        report_id = request.POST.get("report_id")  # Получаем ID отчета

        if not report_id:
            return JsonResponse({"error": "Не указан ID отчета"}, status=400)

        try:
            report = Report.objects.get(id=report_id)
        except Report.DoesNotExist:
            return JsonResponse({"error": "Отчет не найден"}, status=404)

        # Проверяем, не больше ли 5 картинок у отчета
        if report.images.count() >= 5:
            return JsonResponse({"error": "Нельзя загружать больше 5 изображений"}, status=400)

        # Создаем папку с ID отчета
        folder_path = f"reports/{report_id}/"
        if not default_storage.exists(folder_path):
            os.makedirs(default_storage.path(folder_path), exist_ok=True)

        # Сохраняем файл в папку отчета
        file_name = f"{folder_path}{file.name}"
        saved_path = default_storage.save(file_name, ContentFile(file.read()))

        # Создаем объект ReportImage
        report_image = ReportImage.objects.create(report=report, image=saved_path)

        return JsonResponse({"status": "success", "file_url": report_image.image.url})

    return JsonResponse({"error": "Файл не найден"}, status=400)
