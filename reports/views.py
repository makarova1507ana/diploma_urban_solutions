from django.views.generic import TemplateView, DetailView, ListView
from django.shortcuts import redirect, render
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from time import sleep
from django.db.models import Q

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
        Добавление связанных отчетов к теме. Выбираются случайные 5 отчетов.
        """
        context = super().get_context_data(**kwargs)
        topic = context['topic']
        related_reports = Report.objects.filter(category=topic).order_by('?')[:3]  # Получаем 3 случайных отчета
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

# Страница с картой (для отображения географической информации)
class Map(TemplateView):
    template_name = 'map.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        queryset = Report.objects.all()

        # Фильтрация отчётов со статусом "на модерации":
        moderation_status = 'in_moderation'
        if self.request.user.is_authenticated:
            # Для авторизованных пользователей: отчеты на модерации показываются, только если они принадлежат текущему пользователю
            queryset = queryset.exclude(Q(status=moderation_status) & ~Q(user=self.request.user))
        else:
            # Для неавторизованных пользователей: полностью исключаем отчеты на модерации
            queryset = queryset.exclude(status=moderation_status)

        context['reports'] = queryset  # Список всех отчетов
        return context

# Страница с перечнем всех отчетов с возможностью фильтрации
class Reports(ListView):
    model = Report
    template_name = 'reports.html'
    context_object_name = 'reports'
    paginate_by = 10  # Количество отчетов на одной странице
    ordering = ['-updated_at']  # Сортировка по дате создания (по убыванию)

    def get_queryset(self):
        """
        Фильтрация отчетов по статусу, категории, времени создания и поиску по названию и описанию.
        """
        queryset = Report.objects.all()
        queryset = queryset.order_by('-updated_at')

        # Поиск по части текста в названии и описании
        search_query = self.request.GET.get('text')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) | Q(description__icontains=search_query)
            )

        # Фильтрация по статусу
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        # Фильтрация по категории
        category = self.request.GET.get('category')
        if category and category != "None":  # Проверка на None
            queryset = queryset.filter(category__id=category)

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

        # Фильтрация отчётов со статусом "на модерации":
        moderation_status = 'in_moderation'
        if self.request.user.is_authenticated:
            # Для авторизованных пользователей: отчеты на модерации показываются, только если они принадлежат текущему пользователю
            queryset = queryset.exclude(Q(status=moderation_status) & ~Q(user=self.request.user))
        else:
            # Для неавторизованных пользователей: полностью исключаем отчеты на модерации
            queryset = queryset.exclude(status=moderation_status)

        return queryset

    def get_context_data(self, **kwargs):
        """
        Добавление фильтров и доступных статусов/категорий в контекст для отображения в форме.
        """
        context = super().get_context_data(**kwargs)
        context['status_filter'] = self.request.GET.get('status')
        context['category_filter'] = self.request.GET.get('category')
        context['time_filter'] = self.request.GET.get('time_filter')
        context['is_mine'] = self.request.GET.get('is_mine')
        context['search_query'] = self.request.GET.get('text', '')

        # Получаем доступные статусы и категории из модели
        context['statuses'] = Report.STATUS_CHOICES
        context['categories'] = Topic.objects.values_list('id', 'title')

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
        request = self.request

        # Получаем данные из сессии или запроса
        latitude = request.session.get("latitude") or request.GET.get("latitude")
        longitude = request.session.get("longitude") or request.GET.get("longitude")
        selected_topic_id = request.session.get("selected_topic") or request.GET.get("selected_topic")

        # Проверка существования выбранной темы
        topic = None
        if selected_topic_id:
            try:
                topic = Topic.objects.get(pk=int(selected_topic_id))
            except (ValueError, Topic.DoesNotExist):
                topic = None

        # Обратное геокодирование, если адрес отсутствует
        address = request.session.get("address")
        if not address and latitude and longitude:
            address = self.reverse_geocode(latitude, longitude)

        # Передаем данные в контекст
        form = ReportForm(initial={
            'topic_id': selected_topic_id,
            'latitude': latitude,
            'longitude': longitude,
            'address': address,
        })
        context.update({
            "topic": topic,
            "latitude": latitude,
            "longitude": longitude,
            "address": address,
            "location": {"lat": latitude, "lon": longitude, "address": address},
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
        form = ReportForm(request.POST, request.FILES)
        if form.is_valid():
            # Сохранение отчета
            report = form.save(commit=False)
            report.user = request.user
            report.save()

            # Сохранение изображения (если оно есть)
            image = request.FILES.get("image")
            if image:
                ReportImage.objects.create(report=report, image=image)


            messages.success(request, "Ваш отчет успешно создан!")
            return redirect('reports:report_detail', pk=report.id)  # перенаправление на страницу отчета
        else:
            messages.error(request, "Ошибка в данных формы.")
            return redirect(request.path)



