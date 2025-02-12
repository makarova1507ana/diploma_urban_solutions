from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend


# Класс, реализующий аутентификацию по email
class EmailAuthBackend(BaseBackend):
    # Метод для аутентификации пользователя
    def authenticate(self, request, username=None, password=None, **kwargs):
        user_model = get_user_model()
        try:
            # Попытка получить пользователя по email
            user = user_model.objects.get(email=username)

            # Проверка пароля пользователя
            if user.check_password(password):
                return user  # Возвращаем пользователя в случае успешной аутентификации

            return None  # Возвращаем None, если пароль неверен

        except (user_model.DoesNotExist, user_model.MultipleObjectsReturned):
            return None  # Возвращаем None в случае, если пользователя не существует или найдено несколько записей

    # Метод для получения пользователя по его идентификатору
    def get_user(self, user_id):
        user_model = get_user_model()
        try:
            # Попытка получить пользователя по его идентификатору (примари ключу)
            return user_model.objects.get(pk=user_id)
        except user_model.DoesNotExist:
            return None  # Возвращаем None, если пользователя с указанным идентификатором не существует
