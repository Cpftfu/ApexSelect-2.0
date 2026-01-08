from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.contrib import messages
from .models import CustomUser, Vacancy
# Обновляем импорт форм
from .forms import RegistrationForm, LoginForm, VacancyForm
# Создаем формы для админки на месте
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model

User = get_user_model()


# Формы для админки пользователей (определяем здесь)
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


# Существующий админ для пользователей
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm

    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_active', 'is_superuser', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {
            'fields': ('first_name', 'last_name', 'email', 'phone_number', 'date_of_birth', 'bio')
        }),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_verified', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {
            'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_staff', 'is_active'),
        }),
    )

    ordering = ('-date_joined',)
    readonly_fields = ('last_login', 'date_joined', 'created_at', 'updated_at')
    filter_horizontal = ('groups', 'user_permissions',)


# Админ для вакансий
class VacancyAdmin(admin.ModelAdmin):
    form = VacancyForm
    list_display = ('title', 'company', 'location', 'status_display',
                    'employment_type_display', 'salary_display', 'created_at')
    list_filter = ('status', 'employment_type', 'experience', 'is_featured', 'created_at')
    search_fields = ('title', 'company', 'location', 'technologies')
    readonly_fields = ('created_at', 'updated_at', 'published_at')
    ordering = ('-created_at',)
    actions = ['make_published', 'make_closed', 'make_featured']

    fieldsets = (
        (_('Основная информация'), {
            'fields': ('title', 'company', 'location', 'status')
        }),
        (_('Описание вакансии'), {
            'fields': ('short_description', 'full_description', 'requirements',
                       'responsibilities', 'benefits')
        }),
        (_('Детали'), {
            'fields': ('salary_min', 'salary_max', 'currency', 'employment_type',
                       'experience', 'technologies')
        }),
        (_('Дополнительно'), {
            'fields': ('is_featured', 'is_remote', 'is_relocation', 'expires_at')
        }),
        (_('Системная информация'), {
            'classes': ('collapse',),
            'fields': ('created_by', 'created_at', 'updated_at', 'published_at')
        }),
    )

    def status_display(self, obj):
        color = obj.get_status_color()
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            color,
            obj.get_status_display()
        )

    status_display.short_description = _('Статус')

    def employment_type_display(self, obj):
        return obj.get_employment_type_display()

    employment_type_display.short_description = _('Тип занятости')

    def salary_display(self, obj):
        return obj.get_salary_display()

    salary_display.short_description = _('Зарплата')

    def make_published(self, request, queryset):
        updated = queryset.update(status='published')
        self.message_user(request, f'Опубликовано {updated} вакансий', messages.SUCCESS)

    make_published.short_description = _('Опубликовать выбранные')

    def make_closed(self, request, queryset):
        updated = queryset.update(status='closed')
        self.message_user(request, f'Закрыто {updated} вакансий', messages.WARNING)

    make_closed.short_description = _('Закрыть выбранные')

    def make_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'Сделано рекомендуемыми {updated} вакансий', messages.SUCCESS)

    make_featured.short_description = _('Сделать рекомендуемыми')

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


# Регистрация моделей в админке
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Vacancy, VacancyAdmin)