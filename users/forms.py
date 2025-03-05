from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordChangeForm


class LoginUserForm(AuthenticationForm):
    username = forms.CharField(label="Логин",
                    widget=forms.TextInput(attrs={'class': 'form-input'}))
    password = forms.CharField(label="Пароль",
                    widget=forms.PasswordInput(attrs={'class': 'form-input'}))

    class Meta:
        model = get_user_model()
        fields = ['username', 'password']

class RegisterUserForm(UserCreationForm):
    email = forms.EmailField(
        label="E-mail",
        widget=forms.EmailInput(attrs={'class': 'form-input'})
    )
    full_name = forms.CharField(
        label="Полное имя",
        widget=forms.TextInput(attrs={'class': 'form-input'})
    )
    role = forms.CharField(
        label="Роль",
        widget=forms.TextInput(attrs={'class': 'form-input'}),
        required=False
    )
    address = forms.CharField(
        label="Адрес",
        widget=forms.TextInput(attrs={'class': 'form-input'}),
        required=False
    )
    phone_number = forms.CharField(
        label="Номер телефона",
        widget=forms.TextInput(attrs={'class': 'form-input'}),
        required=False
    )
    district = forms.CharField(
        label="Район",
        widget=forms.TextInput(attrs={'class': 'form-input'}),
        required=False
    )
    preferred_contact = forms.ChoiceField(
        label="Предпочитаемый способ связи",
        choices=[
            ('email', 'Email'),
            ('phone', 'Телефон'),
            ('sms', 'СМС'),
        ],
        widget=forms.Select(attrs={'class': 'form-input'})
    )
    password1 = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={'class': 'form-input'})
    )
    password2 = forms.CharField(
        label="Повтор пароля",
        widget=forms.PasswordInput(attrs={'class': 'form-input'})
    )

    class Meta:
        model = get_user_model()
        fields = [
            'email',
            'full_name',
            'role',
            'address',
            'phone_number',
            'district',
            'preferred_contact',
            'password1',
            'password2'
        ]

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if get_user_model().objects.filter(email=email).exists():
            raise forms.ValidationError("Такой E-mail уже существует!")
        return email


class ProfileUserForm(forms.ModelForm):
    email = forms.CharField(label='E-mail', widget=forms.TextInput(attrs={'class': 'form-input'}))
    full_name = forms.CharField(label='ФИО', widget=forms.TextInput(attrs={'class': 'form-input'}))
    address = forms.CharField(label='Адрес', widget=forms.TextInput(attrs={'class': 'form-input'}), required=False)
    phone_number = forms.CharField(label='Телефон', widget=forms.TextInput(attrs={'class': 'form-input'}),
                                   required=False)
    district = forms.CharField(label='Район', widget=forms.TextInput(attrs={'class': 'form-input'}), required=False)
    preferred_contact = forms.ChoiceField(
        label="Предпочитаемый способ связи",
        choices=[('email', 'Email'), ('phone', 'Телефон'), ('sms', 'СМС')],
        widget=forms.Select(attrs={'class': 'form-input'}), required=False
    )

    class Meta:
        model = get_user_model()
        fields = ['email', 'full_name', 'address', 'phone_number', 'district',
                  'preferred_contact']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-input'}),

            'address': forms.Textarea(attrs={'class': 'form-input'}),
        }

class UserPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(label="Старый пароль", widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    new_password1 = forms.CharField(label="Новый пароль", widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    new_password2 = forms.CharField(label="Подтверждение пароля", widget=forms.PasswordInput(attrs={'class': 'form-input'}))
