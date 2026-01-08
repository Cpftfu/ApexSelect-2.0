from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q  # Добавляем импорт Q
from django.utils.timezone import now
from .forms import RegistrationForm, LoginForm, VacancyForm
from .models import Vacancy


# Проверка является ли пользователь администратором
def is_admin(user):
    return user.is_staff or user.is_superuser


# Главная страница с вакансиями
@login_required
def home_view(request):
    # Получаем вакансии
    if request.user.is_staff or request.user.is_superuser:
        # Админы видят все вакансии
        vacancies = Vacancy.objects.all().order_by('-created_at')
    else:
        # Обычные пользователи видят только опубликованные вакансии
        vacancies = Vacancy.objects.filter(status='published').order_by('-created_at')

    return render(request, 'home.html', {
        'user': request.user,
        'vacancies': vacancies,
        'is_admin': request.user.is_staff or request.user.is_superuser
    })


# Страница добавления вакансии (только для админов)
@login_required
@user_passes_test(is_admin, login_url='/')
def add_vacancy_view(request):
    if request.method == 'POST':
        form = VacancyForm(request.POST, user=request.user)
        if form.is_valid():
            vacancy = form.save()
            messages.success(request, f'Вакансия "{vacancy.title}" успешно создана!')
            return redirect('vacancy_list')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = VacancyForm(user=request.user)

    return render(request, 'vacancies/add_vacancy.html', {
        'form': form,
        'title': 'Добавить вакансию'
    })


# Страница редактирования вакансии
@login_required
@user_passes_test(is_admin, login_url='/')
def edit_vacancy_view(request, pk):
    vacancy = get_object_or_404(Vacancy, pk=pk)

    # Проверяем, имеет ли пользователь право редактировать эту вакансию
    if not request.user.is_superuser and vacancy.created_by != request.user:
        messages.error(request, 'У вас нет прав для редактирования этой вакансии.')
        return redirect('vacancy_list')

    if request.method == 'POST':
        form = VacancyForm(request.POST, instance=vacancy, user=request.user)
        if form.is_valid():
            vacancy = form.save()
            messages.success(request, f'Вакансия "{vacancy.title}" успешно обновлена!')
            return redirect('vacancy_list')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = VacancyForm(instance=vacancy, user=request.user)

    return render(request, 'vacancies/add_vacancy.html', {
        'form': form,
        'title': 'Редактировать вакансию',
        'vacancy': vacancy
    })


# Удаление вакансии
@login_required
@user_passes_test(is_admin, login_url='/')
def delete_vacancy_view(request, pk):
    vacancy = get_object_or_404(Vacancy, pk=pk)

    # Проверяем, имеет ли пользователь право удалять эту вакансию
    if not request.user.is_superuser and vacancy.created_by != request.user:
        messages.error(request, 'У вас нет прав для удаления этой вакансии.')
        return redirect('vacancy_list')

    if request.method == 'POST':
        vacancy_title = vacancy.title
        vacancy.delete()
        messages.success(request, f'Вакансия "{vacancy_title}" успешно удалена!')
        return redirect('vacancy_list')

    return render(request, 'vacancies/confirm_delete.html', {
        'vacancy': vacancy
    })


# Детальная страница вакансии
@login_required
def vacancy_detail_view(request, pk):
    vacancy = get_object_or_404(Vacancy, pk=pk)

    # Проверяем доступ к вакансии
    if vacancy.status != 'published' and not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'Эта вакансия не доступна для просмотра.')
        return redirect('home')

    return render(request, 'vacancies/vacancy_detail.html', {
        'vacancy': vacancy,
        'user': request.user
    })


# Список вакансий для админов
@login_required
@user_passes_test(is_admin, login_url='/')
def vacancy_list_view(request):
    vacancies = Vacancy.objects.all().order_by('-created_at')

    # Фильтрация
    status_filter = request.GET.get('status', '')
    if status_filter:
        vacancies = vacancies.filter(status=status_filter)

    search_query = request.GET.get('q', '')
    if search_query:
        vacancies = vacancies.filter(
            Q(title__icontains=search_query) |
            Q(company__icontains=search_query) |
            Q(technologies__icontains=search_query)
        )

    # Вычисляем статистику для отображения
    total = vacancies.count()
    draft_count = vacancies.filter(status='draft').count()
    published_count = vacancies.filter(status='published').count()
    closed_count = vacancies.filter(status='closed').count()
    archived_count = vacancies.filter(status='archived').count()

    return render(request, 'vacancies/vacancy_list.html', {
        'vacancies': vacancies,
        'search_query': search_query,
        'total': total,
        'draft_count': draft_count,
        'published_count': published_count,
        'closed_count': closed_count,
        'archived_count': archived_count,
    })


# Изменение статуса вакансии (AJAX)
@login_required
@user_passes_test(is_admin, login_url='/')
def toggle_vacancy_status(request, pk):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        vacancy = get_object_or_404(Vacancy, pk=pk)

        if not request.user.is_superuser and vacancy.created_by != request.user:
            return JsonResponse({'error': 'Нет прав'}, status=403)

        # Переключаем статус между опубликовано/черновик
        if vacancy.status == 'published':
            vacancy.status = 'draft'
        else:
            vacancy.status = 'published'
            if not vacancy.published_at:
                vacancy.published_at = now()

        vacancy.save()

        return JsonResponse({
            'success': True,
            'new_status': vacancy.status,
            'new_status_display': vacancy.get_status_display(),
            'status_color': vacancy.get_status_color()
        })

    return JsonResponse({'error': 'Неверный запрос'}, status=400)


# Существующие функции аутентификации
def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('home')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = RegistrationForm()

    return render(request, 'registration/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Вы успешно вошли в систему!')
                next_url = request.GET.get('next', 'home')
                return redirect(next_url)
        else:
            messages.error(request, 'Неверное имя пользователя или пароль.')
    else:
        form = LoginForm()

    return render(request, 'registration/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы.')
    return redirect('login')