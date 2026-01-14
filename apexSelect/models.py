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

    # Счетчик откликов
    response_count = models.IntegerField(_('Количество откликов'), default=0)

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
            self.published_at = now()
        super().save(*args, **kwargs)


# НОВАЯ МОДЕЛЬ: Отклики на вакансии
class VacancyResponse(models.Model):
    # Статусы отклика
    STATUS_CHOICES = [
        ('pending', _('На рассмотрении')),
        ('viewed', _('Просмотрено')),
        ('invited', _('Приглашение на собеседование')),
        ('rejected', _('Отказ')),
        ('accepted', _('Принято')),
    ]

    # Связи
    vacancy = models.ForeignKey(
        Vacancy,
        on_delete=models.CASCADE,
        related_name='responses',
        verbose_name=_('Вакансия')
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='vacancy_responses',
        verbose_name=_('Пользователь')
    )

    # Сообщение от пользователя
    cover_letter = models.TextField(
        _('Сопроводительное письмо'),
        max_length=2000,
        blank=True,
        help_text=_('Расскажите, почему вы подходите для этой вакансии')
    )

    # Статус отклика
    status = models.CharField(
        _('Статус отклика'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    # Даты
    created_at = models.DateTimeField(_('Дата отклика'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Дата обновления'), auto_now=True)

    # Административные заметки
    admin_notes = models.TextField(
        _('Заметки администратора'),
        blank=True,
        help_text=_('Внутренние заметки по отклику')
    )

    class Meta:
        verbose_name = _('Отклик на вакансию')
        verbose_name_plural = _('Отклики на вакансии')
        ordering = ['-created_at']
        unique_together = ['vacancy', 'user']  # Один пользователь может откликнуться на вакансию только один раз

    def __str__(self):
        return f"{self.user.username} → {self.vacancy.title}"

    def get_status_color(self):
        """Цвет для отображения статуса отклика"""
        colors = {
            'pending': 'secondary',
            'viewed': 'info',
            'invited': 'success',
            'rejected': 'danger',
            'accepted': 'success',
        }
        return colors.get(self.status, 'secondary')

    def save(self, *args, **kwargs):
        # При создании нового отклика увеличиваем счетчик в вакансии
        if not self.pk:
            self.vacancy.response_count += 1
            self.vacancy.save(update_fields=['response_count'])
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # При удалении отклика уменьшаем счетчик в вакансии
        self.vacancy.response_count -= 1
        self.vacancy.save(update_fields=['response_count'])
        super().delete(*args, **kwargs)


class VacancyResponse(models.Model):
    # Добавим новые статусы для рекрутера
    RECRUITER_STATUS_CHOICES = [
        ('new', _('Новый')),
        ('screening', _('Скрининг')),
        ('interview', _('Интервью')),
        ('technical', _('Техническое собеседование')),
        ('offer', _('Оффер')),
        ('hired', _('Принят')),
        ('rejected', _('Отказ')),
        ('no_response', _('Нет ответа')),
    ]

    vacancy = models.ForeignKey(
        Vacancy,
        on_delete=models.CASCADE,
        related_name='responses',
        verbose_name=_('Вакансия')
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='vacancy_responses',
        verbose_name=_('Пользователь')
    )
    cover_letter = models.TextField(
        _('Сопроводительное письмо'),
        max_length=2000,
        blank=True,
        help_text=_('Расскажите, почему вы подходите для этой вакансии')
    )
    status = models.CharField(
        _('Статус отклика'),
        max_length=20,
        choices=VacancyResponse.STATUS_CHOICES,
        default='pending'
    )
    recruiter_status = models.CharField(
        _('Статус рекрутера'),
        max_length=20,
        choices=RECRUITER_STATUS_CHOICES,
        default='new',
        help_text=_('Статус кандидата в процессе найма')
    )
    recruiter_notes = models.TextField(
        _('Заметки рекрутера'),
        blank=True,
        help_text=_('Внутренние заметки по кандидату')
    )
    interview_date = models.DateTimeField(
        _('Дата собеседования'),
        null=True,
        blank=True
    )
    salary_offer = models.IntegerField(
        _('Предложенная зарплата'),
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(_('Дата отклика'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Дата обновления'), auto_now=True)
    admin_notes = models.TextField(
        _('Заметки администратора'),
        blank=True,
        help_text=_('Внутренние заметки по отклику')
    )

    class Meta:
        verbose_name = _('Отклик на вакансию')
        verbose_name_plural = _('Отклики на вакансии')
        ordering = ['-created_at']
        unique_together = ['vacancy', 'user']

    def __str__(self):
        return f"{self.user.username} → {self.vacancy.title}"

    def get_status_color(self):
        colors = {
            'pending': 'secondary',
            'viewed': 'info',
            'invited': 'success',
            'rejected': 'danger',
            'accepted': 'success',
        }
        return colors.get(self.status, 'secondary')

    def get_recruiter_status_color(self):
        colors = {
            'new': 'info',
            'screening': 'primary',
            'interview': 'warning',
            'technical': 'warning',
            'offer': 'success',
            'hired': 'success',
            'rejected': 'danger',
            'no_response': 'secondary',
        }
        return colors.get(self.recruiter_status, 'secondary')

    def save(self, *args, **kwargs):
        if not self.pk:
            self.vacancy.response_count += 1
            self.vacancy.save(update_fields=['response_count'])
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.vacancy.response_count -= 1
        self.vacancy.save(update_fields=['response_count'])
        super().delete(*args, **kwargs)