from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import Vacancy

User = get_user_model()


# Формы для аутентификации
class RegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите ваш email'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Пользователь с таким email уже существует.")
        return email


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите имя пользователя или email'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


# Формы для админки пользователей
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'password1' in self.fields:
            self.fields['password1'].required = True
        if 'password2' in self.fields:
            self.fields['password2'].required = True


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'password' in self.fields:
            self.fields['password'].help_text = (
                "Пароли хранятся в зашифрованном виде. "
                "Вы не можете увидеть пароль этого пользователя, но можете "
                "изменить его с помощью <a href=\"../password/\">этой формы</a>."
            )


# Форма для вакансий
class VacancyForm(forms.ModelForm):
    class Meta:
        model = Vacancy
        fields = [
            'title', 'company', 'location', 'short_description',
            'full_description', 'requirements', 'responsibilities',
            'benefits', 'salary_min', 'salary_max', 'currency',
            'employment_type', 'experience', 'technologies',
            'status', 'is_featured', 'is_remote', 'is_relocation',
            'expires_at'
        ]
        widgets = {
            'expires_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'short_description': forms.Textarea(attrs={'rows': 3}),
            'full_description': forms.Textarea(attrs={'rows': 8}),
            'requirements': forms.Textarea(attrs={'rows': 6}),
            'responsibilities': forms.Textarea(attrs={'rows': 6}),
            'benefits': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Настройка полей для crispy forms
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

            # Особые настройки для полей
            if field_name in ['is_featured', 'is_remote', 'is_relocation']:
                field.widget.attrs['class'] = 'form-check-input'
            elif field_name in ['employment_type', 'experience', 'status']:
                field.widget.attrs['class'] = 'form-select'
            elif field_name in ['salary_min', 'salary_max']:
                field.widget.attrs['placeholder'] = '0'
            elif field_name == 'technologies':
                field.widget.attrs['placeholder'] = 'Python, Django, PostgreSQL...'

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user and not instance.pk:
            instance.created_by = self.user
        if commit:
            instance.save()
        return instance