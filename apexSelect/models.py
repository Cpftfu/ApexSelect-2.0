from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now
from django.conf import settings


class CustomUser(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)
    phone_number = models.CharField(_('phone number'), max_length=15, blank=True, null=True)
    date_of_birth = models.DateField(_('date of birth'), blank=True, null=True)
    bio = models.TextField(_('biography'), max_length=500, blank=True)

    # Только для администратора
    is_verified = models.BooleanField(_('verified'), default=False)

    # Автоматические поля с дефолтными значениями
    created_at = models.DateTimeField(_('created at'), default=now)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    def __str__(self):
        return f"{self.username} ({self.email})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['-date_joined']


class Vacancy(models.Model):
    # Статусы вакансии
    STATUS_CHOICES = [
        ('draft', _('Черновик')),
        ('published', _('Опубликована')),
        ('closed', _('Закрыта')),
        ('archived', _('В архиве')),
    ]

    # Типы занятости
    EMPLOYMENT_TYPE_CHOICES = [
        ('full_time', _('Полная занятость')),
        ('part_time', _('Частичная занятость')),
        ('remote', _('Удаленная работа')),
        ('freelance', _('Фриланс')),
        ('internship', _('Стажировка')),
    ]

    # Уровень опыта
    EXPERIENCE_CHOICES = [
        ('no_experience', _('Без опыта')),
        ('junior', _('Junior')),
        ('middle', _('Middle')),
        ('senior', _('Senior')),
        ('lead', _('Lead')),
    ]

    # Основные поля
    title = models.CharField(_('Название вакансии'), max_length=200)
    company = models.CharField(_('Компания'), max_length=200)
    location = models.CharField(_('Локация'), max_length=200, default='Москва')

    # Описание
    short_description = models.TextField(_('Краткое описание'), max_length=500)
    full_description = models.TextField(_('Полное описание'))
    requirements = models.TextField(_('Требования'))
    responsibilities = models.TextField(_('Обязанности'))
    benefits = models.TextField(_('Условия и бонусы'), blank=True)

    # Зарплата
    salary_min = models.IntegerField(_('Зарплата от'), null=True, blank=True)
    salary_max = models.IntegerField(_('Зарплата до'), null=True, blank=True)
    currency = models.CharField(_('Валюта'), max_length=10, default='руб.')

    # Категории
    employment_type = models.CharField(
        _('Тип занятости'),
        max_length=20,
        choices=EMPLOYMENT_TYPE_CHOICES,
        default='full_time'
    )
    experience = models.CharField(
        _('Требуемый опыт'),
        max_length=20,
        choices=EXPERIENCE_CHOICES,
        default='no_experience'
    )

    # Технологии
    technologies = models.CharField(_('Технологии'), max_length=500, blank=True,
                                    help_text=_('Укажите технологии через запятую'))

    # Статус
    status = models.CharField(
        _('Статус'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )

    # Связь с вашей моделью CustomUser
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Это ссылка на CustomUser из настроек
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='vacancies',
        verbose_name=_('Создатель')
    )

    # Даты
    published_at = models.DateTimeField(_('Дата публикации'), null=True, blank=True)
    expires_at = models.DateTimeField(_('Действует до'), null=True, blank=True)
    created_at = models.DateTimeField(_('Дата создания'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Дата обновления'), auto_now=True)

    # Флаги
    is_featured = models.BooleanField(_('Рекомендуемая'), default=False)
    is_remote = models.BooleanField(_('Удаленная работа'), default=False)
    is_relocation = models.BooleanField(_('Релокация'), default=False)
    is_active = models.BooleanField(_('Активна'), default=True)

    class Meta:
        verbose_name = _('Вакансия')
        verbose_name_plural = _('Вакансии')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.company}"

    def get_salary_display(self):
        """Форматированное отображение зарплаты"""
        if self.salary_min and self.salary_max:
            return f"{self.salary_min:,} - {self.salary_max:,} {self.currency}".replace(',', ' ')
        elif self.salary_min:
            return f"от {self.salary_min:,} {self.currency}".replace(',', ' ')
        elif self.salary_max:
            return f"до {self.salary_max:,} {self.currency}".replace(',', ' ')
        return _('По договоренности')

    def get_status_color(self):
        """Цвет для отображения статуса"""
        colors = {
            'draft': 'secondary',
            'published': 'success',
            'closed': 'warning',
            'archived': 'dark',
        }
        return colors.get(self.status, 'secondary')

    def save(self, *args, **kwargs):
        # Автоматически устанавливаем published_at при публикации
        if self.status == 'published' and not self.published_at:
            from django.utils.timezone import now
            self.published_at = now()
        super().save(*args, **kwargs)