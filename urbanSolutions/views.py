from django.views.generic.base import TemplateView

class Index(TemplateView):

    template_name = 'index.html'


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