from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import Vacancy, VacancyResponse

User = get_user_model()


class RegistrationForm(UserCreationForm):
    username = forms.CharField(
        label='Имя пользователя',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Придумайте имя пользователя',
            'autofocus': 'autofocus'
        }),
        help_text='Обязательное поле. Не более 150 символов. Только буквы, цифры и символы @/./+/-/_.',
        error_messages={
            'required': 'Пожалуйста, введите имя пользователя',
            'max_length': 'Имя пользователя не должно превышать 150 символов',
            'invalid': 'Имя пользователя содержит недопустимые символы'
        }
    )

    email = forms.EmailField(
        label='Электронная почта',
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'example@email.com'
        }),
        error_messages={
            'required': 'Пожалуйста, введите email',
            'invalid': 'Введите корректный email адрес'
        }
    )

    password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Создайте надежный пароль'
        }),
        help_text='''
        <div class="password-requirements">
            <p class="mb-1"><small>Пароль должен соответствовать требованиям:</small></p>
            <ul class="small text-muted mb-0">
                <li>Не менее 8 символов</li>
                <li>Не должен быть слишком простым</li>
                <li>Не должен состоять только из цифр</li>
                <li>Не должен быть похож на другую личную информацию</li>
            </ul>
        </div>
        ''',
        error_messages={
            'required': 'Пожалуйста, введите пароль'
        }
    )

    password2 = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Повторите пароль для подтверждения'
        }),
        help_text='Для подтверждения введите тот же пароль еще раз.',
        error_messages={
            'required': 'Пожалуйста, подтвердите пароль'
        }
    )

    first_name = forms.CharField(
        label='Имя',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ваше имя (необязательно)'
        })
    )

    last_name = forms.CharField(
        label='Фамилия',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ваша фамилия (необязательно)'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
        labels = {
            'username': 'Имя пользователя',
            'email': 'Электронная почта',
            'first_name': 'Имя',
            'last_name': 'Фамилия',
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Пользователь с таким email уже зарегистрирован.")
        return email

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Убираем стандартные английские сообщения
        self.fields[
            'username'].help_text = 'Обязательное поле. Не более 150 символов. Только буквы, цифры и символы @/./+/-/_.'
        self.fields['password1'].help_text = '''
        <div class="password-requirements">
            <p class="mb-1"><small>Пароль должен соответствовать требованиям:</small></p>
            <ul class="small text-muted mb-0">
                <li>Не менее 8 символов</li>
                <li>Не должен быть слишком простым</li>
                <li>Не должен состоять только из цифр</li>
                <li>Не должен быть похож на другую личную информацию</li>
            </ul>
        </div>
        '''


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


# ============ НОВЫЕ ФОРМЫ ДЛЯ ПРОФИЛЯ ============

class UserProfileForm(forms.ModelForm):
    """Форма для редактирования профиля пользователя"""

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите ваше имя'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите вашу фамилию'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите ваш email'
            }),
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите имя пользователя'
            }),
        }
        labels = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'email': 'Электронная почта',
            'username': 'Имя пользователя',
        }
        help_texts = {
            'username': 'Обязательное поле. Не более 150 символов. Только буквы, цифры и символы @/./+/-/_.',
        }

    def clean_email(self):
        """Проверка уникальности email (исключая текущего пользователя)"""
        email = self.cleaned_data.get('email')
        if email and self.instance:
            # Проверяем, есть ли другой пользователь с таким email
            if User.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
                raise ValidationError("Пользователь с таким email уже существует.")
        return email

    def clean_username(self):
        """Проверка уникальности username (исключая текущего пользователя)"""
        username = self.cleaned_data.get('username')
        if username and self.instance:
            # Проверяем, есть ли другой пользователь с таким username
            if User.objects.exclude(pk=self.instance.pk).filter(username=username).exists():
                raise ValidationError("Пользователь с таким именем уже существует.")
        return username


class ChangePasswordForm(forms.Form):
    """Форма для смены пароля"""

    old_password = forms.CharField(
        label='Текущий пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите текущий пароль'
        }),
        error_messages={
            'required': 'Пожалуйста, введите текущий пароль'
        }
    )

    new_password1 = forms.CharField(
        label='Новый пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите новый пароль'
        }),
        help_text='''
        <div class="password-requirements">
            <p class="mb-1"><small>Требования к паролю:</small></p>
            <ul class="small text-muted mb-0">
                <li>Не менее 8 символов</li>
                <li>Не должен быть слишком простым</li>
                <li>Не должен состоять только из цифр</li>
            </ul>
        </div>
        ''',
        error_messages={
            'required': 'Пожалуйста, введите новый пароль'
        }
    )

    new_password2 = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Повторите новый пароль'
        }),
        help_text='Для подтверждения введите тот же пароль еще раз.',
        error_messages={
            'required': 'Пожалуйста, подтвердите новый пароль'
        }
    )

    def clean_new_password2(self):
        """Проверка совпадения паролей"""
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')

        if password1 and password2 and password1 != password2:
            raise ValidationError("Пароли не совпадают.")

        # Здесь можно добавить дополнительные проверки сложности пароля
        if len(password1) < 8:
            raise ValidationError("Пароль должен содержать не менее 8 символов.")

        if password1.isdigit():
            raise ValidationError("Пароль не может состоять только из цифр.")

        return password2


class AvatarUploadForm(forms.Form):
    """Форма для загрузки аватарки (если планируете добавить)"""

    avatar = forms.ImageField(
        label='Аватар',
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        }),
        help_text='Загрузите изображение (JPEG, PNG, GIF)'
    )

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')

        if avatar:
            # Проверка размера файла (макс 2MB)
            if avatar.size > 2 * 1024 * 1024:
                raise ValidationError("Размер файла не должен превышать 2MB.")

            # Проверка типа файла
            if not avatar.content_type.startswith('image/'):
                raise ValidationError("Файл должен быть изображением.")

        return avatar


class NotificationSettingsForm(forms.Form):
    """Форма для настроек уведомлений (если нужно)"""

    email_notifications = forms.BooleanField(
        label='Получать уведомления по email',
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

    response_notifications = forms.BooleanField(
        label='Уведомлять о новых откликах',
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

    status_notifications = forms.BooleanField(
        label='Уведомлять об изменении статуса отклика',
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )


# ============ ОСТАЛЬНЫЕ ФОРМЫ ============

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

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

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


class VacancyResponseForm(forms.ModelForm):
    class Meta:
        model = VacancyResponse
        fields = ['cover_letter']
        widgets = {
            'cover_letter': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': _('Расскажите, почему вы подходите для этой вакансии...')
            }),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.vacancy = kwargs.pop('vacancy', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()

        if self.user and self.vacancy:
            if VacancyResponse.objects.filter(
                    user=self.user,
                    vacancy=self.vacancy
            ).exists():
                raise ValidationError(_('Вы уже откликнулись на эту вакансию.'))

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:
            instance.user = self.user
        if self.vacancy:
            instance.vacancy = self.vacancy

        if commit:
            instance.save()

        return instance


class RecruiterResponseForm(forms.ModelForm):
    class Meta:
        model = VacancyResponse
        fields = ['recruiter_status', 'recruiter_notes', 'interview_date', 'salary_offer']
        widgets = {
            'recruiter_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Заметки по кандидату...'
            }),
            'interview_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'salary_offer': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Предложенная зарплата'
            }),
            'recruiter_status': forms.Select(attrs={
                'class': 'form-select'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Кастомизируем labels
        self.fields['recruiter_status'].label = 'Статус в процессе найма'
        self.fields['recruiter_notes'].label = 'Заметки рекрутера'
        self.fields['interview_date'].label = 'Дата собеседования'
        self.fields['salary_offer'].label = 'Предложенная зарплата'