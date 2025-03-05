
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, UpdateView
from django.db.models import Count

from reports.models import Report
from .forms import LoginUserForm, RegisterUserForm, UserPasswordChangeForm, ProfileUserForm

# страница для входа пользователя
class LoginUser(LoginView):
    form_class = LoginUserForm  # Используемая форма для входа
    template_name = 'users/login.html'  # Шаблон страницы входа
    extra_context = {'title': 'Авторизация'}  # Дополнительные контекстные данные

    def get_success_url(self):
        return reverse_lazy('index')  # Перенаправление пользователя после успешного входа

# страница для регистрации пользователя
class RegisterUser(CreateView):
    form_class = RegisterUserForm  # Используемая форма для регистрации
    template_name = 'users/register.html'  # Шаблон страницы регистрации
    extra_context = {'title': "Регистрация"}  # Дополнительные контекстные данные
    success_url = reverse_lazy('users:login')  # Перенаправление пользователя после успешной регистрации

# страница для просмотра и редактирования профиля пользователя
class ProfileUser(LoginRequiredMixin, UpdateView):
    model = get_user_model()  # Используемая модель пользователя
    form_class = ProfileUserForm  # Используемая форма для редактирования профиля
    template_name = 'users/profile.html'  # Шаблон страницы профиля
    extra_context = {'title': "Профиль пользователя"}  # Дополнительные контекстные данные

    def get_success_url(self):
        return reverse_lazy('users:profile')  # Перенаправление пользователя после успешного обновления профиля

    def get_object(self, queryset=None):
        return self.request.user  # Получение объекта пользователя для редактирования

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Получение всех отчетов пользователя
        user_reports = Report.objects.filter(user=self.request.user)

        # Подсчет общего количества отчетов и количества отчетов в разных статусах
        report_counts = user_reports.values('status').annotate(count=Count('id')).order_by('status')

        total_reports = user_reports.count()
        status_counts = {status['status']: status['count'] for status in report_counts}

        # Добавляем данные в контекст
        context['user_reports'] = user_reports
        context['total_reports'] = total_reports
        context['status_counts'] = status_counts  # Словарь вида: {статус: количество}

        return context

# страница для изменения пароля пользователя
class UserPasswordChange(PasswordChangeView):
    form_class = UserPasswordChangeForm  # Используемая форма для изменения пароля
    success_url = reverse_lazy("users:password_change_done")  # Перенаправление пользователя после успешного изменения пароля
    template_name = "users/password_change_form.html"  # Шаблон страницы изменения пароля
