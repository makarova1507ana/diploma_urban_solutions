from django.views.generic import TemplateView, DetailView
from django.shortcuts import redirect, render
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from time import sleep
from .models import Report, ReportImage, Topic

class TopicsPage(TemplateView):
    template_name = 'topics.html'

    def get_context_data(self, **kwargs):
        # Получаем все темы из базы данных
        topics = Topic.objects.all()

        # Добавляем темы в контекст
        context = super().get_context_data(**kwargs)
        context['topics'] = topics
        return context

class TopicDetailView(DetailView):
    model = Topic
    template_name = 'topic_detail.html'
    context_object_name = 'topic'

class Step1View(TemplateView):
    template_name = 'step1.html'

    def post(self, request, *args, **kwargs):
        lat = request.POST.get('lat')
        lon = request.POST.get('lon')

        # Сохраняем координаты в сессии
        request.session['lat'] = lat
        request.session['lon'] = lon

        # Переадресация на второй этап
        return redirect('reports:step2')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hide_report_button'] = True  # Скрываем кнопку
        return context


class Step2View(TemplateView):
    template_name = 'step2.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hide_report_button'] = True  # Скрываем кнопку
        context['topics'] = Topic.objects.all()  # Передаем список тем
        return context

    def post(self, request, *args, **kwargs):
        selected_topic = request.POST.get('selected_topic')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')

        # Сохраняем выбранную тему и координаты в сессии
        request.session['selected_topic'] = selected_topic
        request.session['latitude'] = latitude
        request.session['longitude'] = longitude

        # Переход к step3
        return redirect('reports:step3')



class Step3View(TemplateView):
    template_name = 'step3.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Получаем данные из GET-запроса
        selected_topic_id = self.request.GET.get('selected_topic')
        latitude = self.request.GET.get('latitude')
        longitude = self.request.GET.get('longitude')

        # Проверяем, что полученные данные существуют и корректны
        topic = None
        if selected_topic_id:
            try:
                topic = Topic.objects.get(pk=int(selected_topic_id))
            except (ValueError, Topic.DoesNotExist):
                topic = None

        # Геокодирование с проверкой на ошибки
        address = self.reverse_geocode(latitude, longitude) if latitude and longitude else "Адрес не найден"

        # Передаем данные в контекст
        context.update({
            'topic': topic,
            'latitude': latitude,
            'longitude': longitude,
            'address': address,
        })
        return context

    def reverse_geocode(self, latitude, longitude, retries=3):
        """Функция для обратного геокодирования с повторными попытками при таймаутах."""
        if not latitude or not longitude:
            return "Адрес не найден"

        geolocator = Nominatim(user_agent="my_geocoder_app_12345")
        for attempt in range(retries):
            try:
                # Формируем запрос для геокодирования
                location = geolocator.reverse(f"{latitude}, {longitude}", exactly_one=True)
                if location and location.address:
                    return location.address
            except GeocoderTimedOut:
                # Подождем перед повторной попыткой в случае таймаута
                sleep(2)
            except Exception as e:
                # Логирование ошибок (для отладки)
                print(f"Ошибка геокодирования: {e}")
        return "Адрес не найден"


    def post(self, request, *args, **kwargs):
        # Получаем данные из формы
        selected_topic_id = request.POST.get('topic_id')  # Передаем ID, а не title
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        description = request.POST.get('description', '').strip()
        images = request.FILES.getlist('images')

        # Проверяем, что данные корректно переданы
        if not selected_topic_id:
            return self.render_to_response({"error": "Выберите тему."})

        # Сохраняем данные в сессии
        request.session['selected_topic'] = selected_topic_id
        request.session['latitude'] = latitude
        request.session['longitude'] = longitude

        # Получаем тему
        topic = Topic.objects.filter(id=selected_topic_id).first()

        # Если тема не найдена, вернем ошибку
        if not topic:
            return self.render_to_response({"error": "Тема не найдена."})

        # Создание отчета
        report = Report.objects.create(
            user=request.user,
            category=topic,
            title=topic.title if topic else "Без категории",
            description=description if description else None,
            latitude=latitude,
            longitude=longitude,
            address=self.reverse_geocode(latitude, longitude)
        )

        # Сохранение изображений (максимум 5)
        allowed_formats = {'image/jpeg', 'image/png', 'image/heic', 'image/heif'}
        max_size = 5 * 1024 * 1024  # 5 MB

        for image in images[:5]:
            if image.content_type in allowed_formats and image.size <= max_size:
                file_path = f"reports/{report.id}/{image.name}"
                saved_path = default_storage.save(file_path, ContentFile(image.read()))
                ReportImage.objects.create(report=report, image=saved_path)

        return redirect('index')



