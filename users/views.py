# from django.contrib.auth.decorators import login_required
# from django.contrib.auth.forms import AuthenticationForm
# from django.contrib.auth.views import LoginView, LogoutView
# from django.http import HttpResponse
# from django.shortcuts import render
# from django.urls import reverse_lazy
# from django.views.generic import CreateView
#
# from users.forms import LoginUserForm, RegisterUserForm
#
#
# class LoginUser(LoginView):
#     form_class = LoginUserForm #LoginUserForm - немного модифицировали  / AuthenticationForm - это стандатрнтная форма
#     template_name = 'users/sign_in.html'
#
#     def get_success_url(self):
#         return '/' #reverse_lazy('home')
#
# # class LogoutUser(LogoutView):
# #     def get_success_url(self):
# #         return '../../' # костыльный выход на главную страницу
# class RegisterUser(CreateView):
#     form_class = RegisterUserForm
#     template_name = 'users/registration.html'
#
#     def get_success_url(self):
#         return '/users/login/' #reverse_lazy('home')
#
# @login_required(login_url='/users/login/') #login_url- неавтор. пол. отравляем на авторизацию
# def account(request):
#     # только авторизованным пользователям доступна страница
#     return render(request, 'users/account.html')
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, UpdateView

from .forms import LoginUserForm, RegisterUserForm, UserPasswordChangeForm, ProfileUserForm

# страница для входа пользователя
class LoginUser(LoginView):
    form_class = LoginUserForm  # Используемая форма для входа
    template_name = 'users/login.html'  # Шаблон страницы входа
    extra_context = {'title': 'Авторизация'}  # Дополнительные контекстные данные

    def get_success_url(self):
        return reverse_lazy('problems:index')  # Перенаправление пользователя после успешного входа

# страница для просмотра учетной записи пользователя (требует авторизации)
@login_required(login_url='/users/login/')  # Перенаправление неавторизованных пользователей
def account(request):
    # только авторизованным пользователям доступна страница
    return render(request, 'users/account.html')

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

# страница для изменения пароля пользователя
class UserPasswordChange(PasswordChangeView):
    form_class = UserPasswordChangeForm  # Используемая форма для изменения пароля
    success_url = reverse_lazy("users:password_change_done")  # Перенаправление пользователя после успешного изменения пароля
    template_name = "users/password_change_form.html"  # Шаблон страницы изменения пароля
