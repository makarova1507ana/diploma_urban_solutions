from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from .models import Report, Topic, Comment, ReportImage
from django.contrib.messages import get_messages
# tests.py
from django.core.mail import outbox
from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Report, Topic


class ReportStatusChangeTestCase(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser', password='password123', email='testuser@example.com'
        )
        self.topic = Topic.objects.create(title="Test Topic")
        self.report = Report.objects.create(
            title="Test Report",
            description="Test description",
            category=self.topic,
            user=self.user,
            status="new",
        )

    def test_status_change_email(self):
        """Проверка отправки письма при изменении статуса"""
        self.report.status = "in_progress"
        self.report.save()  # Сохранение объекта вызовет изменение статуса

        # Проверка, что письмо было отправлено
        self.assertEqual(len(outbox), 1)  # Один email в outbox
        self.assertEqual(outbox[0].subject, 'Изменение статуса заявки: Test Report')
        self.assertIn("Статус вашей заявки 'Test Report' был изменен на: В процессе", outbox[0].body)
        self.assertEqual(outbox[0].to, ['testuser@example.com'])


class ReportTestCase(TestCase):

    def setUp(self):
        # Создаем тестового пользователя
        self.user = get_user_model().objects.create_user(
            username='makarova1507nastya@gmail.com', password='Gfhjkm9('
        )

        # Создаем тестовую тему
        self.topic = Topic.objects.create(title="Test Topic")

        # Создаем тестовый отчет
        self.report = Report.objects.create(
            title="Test Report",
            description="Test description",
            category=self.topic,
            user=self.user,
            status="new",
            created_at=timezone.now(),
            updated_at=timezone.now()
        )

    def test_report_detail_view(self):
        """Проверка отображения страницы с деталями отчета"""
        url = reverse('reports:report_detail', kwargs={'pk': self.report.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'report.html')
        self.assertContains(response, self.report.title)
        self.assertContains(response, self.report.description)

    def test_add_comment(self):
        """Проверка добавления комментария к отчету"""
        self.client.login(username='testuser', password='password123')

        comment_data = {'text': 'Test comment'}
        url = reverse('reports:add_comment', kwargs={'report_id': self.report.id})
        response = self.client.post(url, comment_data)

        # Проверяем, что комментарий добавлен
        self.assertEqual(response.status_code, 302)  # Redirect после добавления комментария
        self.assertRedirects(response, reverse('reports:report_detail', kwargs={'pk': self.report.pk}))

        # Проверяем, что комментарий действительно добавился
        comment = Comment.objects.filter(report=self.report).last()
        self.assertEqual(comment.text, 'Test comment')

    def test_add_comment_with_image(self):
        """Проверка добавления комментария с изображением"""
        self.client.login(username='testuser', password='password123')

        comment_data = {'text': 'Test comment with image'}
        image = SimpleUploadedFile('test_image.jpg', b'file_content', content_type='image/jpeg')
        comment_data['images'] = image

        url = reverse('reports:add_comment', kwargs={'report_id': self.report.id})
        response = self.client.post(url, comment_data)

        # Проверяем, что комментарий с изображением добавлен
        self.assertEqual(response.status_code, 302)  # Redirect после добавления комментария
        self.assertRedirects(response, reverse('reports:report_detail', kwargs={'pk': self.report.pk}))

        # Проверяем, что изображение сохранено
        comment_image = ReportImage.objects.filter(report=self.report).last()
        self.assertIsNotNone(comment_image)
        self.assertEqual(comment_image.image.name.split('/')[-1], 'test_image.jpg')

    def test_filter_reports(self):
        """Проверка фильтрации отчетов по статусу"""
        # Создаем еще один отчет с другим статусом
        report2 = Report.objects.create(
            title="Another Report",
            description="Another description",
            category=self.topic,
            user=self.user,
            status="in_progress",
            created_at=timezone.now(),
            updated_at=timezone.now()
        )

        # Фильтруем отчеты по статусу
        url = reverse('reports:reports_list') + '?status=Новая'
        response = self.client.get(url)

        # Проверяем, что в ответе есть только один отчет
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.report.title)
        self.assertNotContains(response, report2.title)

    def test_add_report_step1(self):
        """Проверка перехода на второй шаг добавления отчета"""
        self.client.login(username='testuser', password='password123')

        data = {'lat': '55.7558', 'lon': '37.6176'}  # Пример координат
        url = reverse('reports:step1')
        response = self.client.post(url, data)

        # Проверяем, что мы переходим ко второму шагу
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('reports:step2'))

    def test_topics_page(self):
        """Проверка отображения страницы с перечнем тем"""
        url = reverse('reports:topics_page')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'topics.html')
        self.assertContains(response, self.topic.title)

    def test_invalid_comment_form(self):
        """Проверка обработки некорректной формы комментария"""
        self.client.login(username='testuser', password='password123')

        # Оставляем текст пустым
        comment_data = {'text': ''}
        url = reverse('reports:add_comment', kwargs={'report_id': self.report.id})
        response = self.client.post(url, comment_data)

        # Проверяем, что форма не прошла валидацию
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'text', 'Это поле обязательно.')

    def test_report_detail_view_not_found(self):
        """Проверка обработки случая, когда отчет не найден"""
        url = reverse('reports:report_detail', kwargs={'pk': 999})  # Несуществующий ID
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class MessageTests(TestCase):

    def test_success_message_on_comment_creation(self):
        """Проверка сообщения об успешном добавлении комментария"""
        self.client.login(username='testuser', password='password123')

        comment_data = {'text': 'Test comment'}
        url = reverse('reports:add_comment', kwargs={'report_id': self.report.id})
        response = self.client.post(url, comment_data)

        # Проверяем, что сообщение об успешном добавлении комментария отображается
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Комментарий успешно добавлен!')

