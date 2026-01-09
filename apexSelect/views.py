from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.db.models import Q, Count
from django.utils.timezone import now
from .forms import RegistrationForm, LoginForm, VacancyForm, VacancyResponseForm
from .models import Vacancy, VacancyResponse, CustomUser


# Проверка является ли пользователь администратором
def is_admin(user):
    return user.is_staff or user.is_superuser


# Главная страница с вакансиями
@login_required
def home_view(request):
    # Фильтрация вакансий
    vacancies = Vacancy.objects.filter(status='published', is_active=True).order_by('-created_at')

    # Поиск
    search_query = request.GET.get('search', '')
    if search_query:
        vacancies = vacancies.filter(
            Q(title__icontains=search_query) |
            Q(company__icontains=search_query) |
            Q(short_description__icontains=search_query) |
            Q(technologies__icontains=search_query)
        )

    # Фильтр по типу занятости
    employment_type = request.GET.get('employment_type', '')
    if employment_type:
        vacancies = vacancies.filter(employment_type=employment_type)

    # Фильтр по опыту
    experience = request.GET.get('experience', '')
    if experience:
        vacancies = vacancies.filter(experience=experience)

    # Фильтр по удаленной работе
    is_remote = request.GET.get('is_remote', '')
    if is_remote == 'true':
        vacancies = vacancies.filter(is_remote=True)

    # Получаем ID вакансий, на которые пользователь уже откликнулся
    user_response_ids = VacancyResponse.objects.filter(
        user=request.user
    ).values_list('vacancy_id', flat=True)

    # Статистика для фильтров
    employment_types = Vacancy.objects.filter(status='published').values_list(
        'employment_type', flat=True
    ).distinct()

    experience_levels = Vacancy.objects.filter(status='published').values_list(
        'experience', flat=True
    ).distinct()

    return render(request, 'home.html', {
        'vacancies': vacancies,
        'is_admin': request.user.is_staff or request.user.is_superuser,
        'user_response_ids': list(user_response_ids),
        'search_query': search_query,
        'employment_type_filter': employment_type,
        'experience_filter': experience,
        'is_remote_filter': is_remote,
        'employment_types': employment_types,
        'experience_levels': experience_levels,
        'total_vacancies': vacancies.count(),
    })


# Страница добавления вакансии (только для админов)
@login_required
@user_passes_test(is_admin)
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
@user_passes_test(is_admin)
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
@user_passes_test(is_admin)
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
    if vacancy.status != 'published' and not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, 'Эта вакансия не доступна для просмотра.')
        return redirect('home')

    # Проверяем, откликался ли пользователь уже на эту вакансию
    has_responded = VacancyResponse.objects.filter(
        user=request.user,
        vacancy=vacancy
    ).exists()

    # Получаем форму отклика
    form = VacancyResponseForm(user=request.user, vacancy=vacancy)

    # Получаем отклики (для админов)
    responses = None
    if request.user.is_staff or request.user.is_superuser:
        responses = VacancyResponse.objects.filter(vacancy=vacancy).select_related('user')

    # Похожие вакансии
    similar_vacancies = Vacancy.objects.filter(
        status='published',
        is_active=True,
        technologies__icontains=vacancy.technologies.split(',')[0] if vacancy.technologies else ''
    ).exclude(pk=pk)[:3]

    return render(request, 'vacancies/vacancy_detail.html', {
        'vacancy': vacancy,
        'has_responded': has_responded,
        'form': form,
        'responses': responses,
        'similar_vacancies': similar_vacancies,
    })


# Отклик на вакансию
@login_required
def respond_to_vacancy_view(request, pk):
    vacancy = get_object_or_404(Vacancy, pk=pk)

    # Проверяем, что вакансия опубликована
    if vacancy.status != 'published':
        messages.error(request, 'На эту вакансию нельзя откликнуться.')
        return redirect('vacancy_detail', pk=pk)

    # Проверяем, не откликался ли пользователь уже
    if VacancyResponse.objects.filter(user=request.user, vacancy=vacancy).exists():
        messages.warning(request, 'Вы уже откликнулись на эту вакансию.')
        return redirect('vacancy_detail', pk=pk)

    if request.method == 'POST':
        form = VacancyResponseForm(request.POST, user=request.user, vacancy=vacancy)
        if form.is_valid():
            response = form.save()
            messages.success(request, 'Ваш отклик успешно отправлен!')
            return redirect('vacancy_detail', pk=pk)
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = VacancyResponseForm(user=request.user, vacancy=vacancy)

    return render(request, 'vacancies/respond_vacancy.html', {
        'vacancy': vacancy,
        'form': form,
    })


@login_required
def my_responses_view(request):
    # Получаем ВАКАНСИИ, на которые пользователь откликнулся
    response_vacancies = Vacancy.objects.filter(
        responses__user=request.user
    ).distinct().order_by('-responses__created_at')

    # Получаем сами отклики для получения статусов
    user_responses = VacancyResponse.objects.filter(
        user=request.user
    ).select_related('vacancy')

    # Создаем список вакансий с информацией об отклике
    vacancies_with_responses = []
    for vacancy in response_vacancies:
        # Находим соответствующий отклик для этой вакансии
        response = user_responses.filter(vacancy=vacancy).first()
        vacancies_with_responses.append({
            'vacancy': vacancy,
            'response': response,
            'response_id': response.id if response else None,
            'status': response.status if response else None,
            'status_display': response.get_status_display() if response else None,
            'status_color': response.get_status_color() if response else None,
            'cover_letter': response.cover_letter if response else '',
            'created_at': response.created_at if response else None,
        })

    # Подсчет откликов по статусам
    pending_count = user_responses.filter(status='pending').count()
    viewed_count = user_responses.filter(status='viewed').count()
    invited_count = user_responses.filter(status='invited').count()
    rejected_count = user_responses.filter(status='rejected').count()
    accepted_count = user_responses.filter(status='accepted').count()

    total_count = len(vacancies_with_responses)

    return render(request, 'vacancies/my_responses.html', {
        'vacancies_with_responses': vacancies_with_responses,
        'total_count': total_count,
        'pending_count': pending_count,
        'viewed_count': viewed_count,
        'invited_count': invited_count,
        'rejected_count': rejected_count,
        'accepted_count': accepted_count,
    })

# Удаление отклика
@login_required
def delete_response_view(request, pk):
    response = get_object_or_404(VacancyResponse, pk=pk)

    # Проверяем, что пользователь имеет право удалить этот отклик
    if response.user != request.user and not (request.user.is_staff or request.user.is_superuser):
        return HttpResponseForbidden("У вас нет прав для удаления этого отклика.")

    if request.method == 'POST':
        vacancy_pk = response.vacancy.pk
        vacancy_title = response.vacancy.title
        response.delete()
        messages.success(request, f'Отклик на вакансию "{vacancy_title}" успешно удален.')
        return redirect('my_responses')

    return render(request, 'vacancies/confirm_delete_response.html', {
        'response': response,
    })


# Изменение статуса отклика (для админов)
@login_required
@user_passes_test(is_admin)
def update_response_status_view(request, pk):
    response = get_object_or_404(VacancyResponse, pk=pk)

    if not request.method == 'POST':
        return HttpResponseBadRequest("Только POST запросы")

    new_status = request.POST.get('status')
    if new_status not in dict(VacancyResponse.STATUS_CHOICES):
        messages.error(request, 'Неверный статус.')
        return redirect('vacancy_responses', pk=response.vacancy.pk)

    response.status = new_status
    response.save()
    messages.success(request, f'Статус отклика изменен на "{response.get_status_display()}"')

    return redirect('vacancy_responses', pk=response.vacancy.pk)


# Просмотр откликов на вакансию (для админов)
@login_required
@user_passes_test(is_admin)
def vacancy_responses_view(request, pk):
    vacancy = get_object_or_404(Vacancy, pk=pk)
    responses = VacancyResponse.objects.filter(vacancy=vacancy).select_related('user')

    # Статистика по откликам
    status_counts = responses.values('status').annotate(count=Count('id'))

    return render(request, 'vacancies/vacancy_responses.html', {
        'vacancy': vacancy,
        'responses': responses,
        'status_counts': status_counts,
    })


# Список вакансий для админов
@login_required
@user_passes_test(is_admin)
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
    draft_count = Vacancy.objects.filter(status='draft').count()
    published_count = Vacancy.objects.filter(status='published').count()
    closed_count = Vacancy.objects.filter(status='closed').count()
    archived_count = Vacancy.objects.filter(status='archived').count()

    return render(request, 'vacancies/vacancy_list.html', {
        'vacancies': vacancies,
        'status_filter': status_filter,
        'search_query': search_query,
        'total': total,
        'draft_count': draft_count,
        'published_count': published_count,
        'closed_count': closed_count,
        'archived_count': archived_count,
    })


# Изменение статуса вакансии (AJAX)
@login_required
@user_passes_test(is_admin)
def toggle_vacancy_status(request, pk):
    if not request.method == 'POST':
        return JsonResponse({'error': 'Неверный метод запроса'}, status=400)

    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'error': 'Не AJAX запрос'}, status=400)

    vacancy = get_object_or_404(Vacancy, pk=pk)

    if not request.user.is_superuser and vacancy.created_by != request.user:
        return JsonResponse({'error': 'Нет прав'}, status=403)

    # Переключаем статус между опубликовано/черновик
    if vacancy.status == 'published':
        vacancy.status = 'draft'
        message = 'Вакансия перемещена в черновики'
    else:
        vacancy.status = 'published'
        if not vacancy.published_at:
            vacancy.published_at = now()
        message = 'Вакансия опубликована'

    vacancy.save()

    return JsonResponse({
        'success': True,
        'message': message,
        'new_status': vacancy.status,
        'new_status_display': vacancy.get_status_display(),
        'status_color': vacancy.get_status_color()
    })


# Регистрация
def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.username}! Регистрация прошла успешно!')
            return redirect('home')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = RegistrationForm()

    return render(request, 'registration/register.html', {'form': form})


# Вход
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
                messages.success(request, f'Добро пожаловать, {user.username}!')
                next_url = request.GET.get('next', 'home')
                return redirect(next_url)
        messages.error(request, 'Неверное имя пользователя или пароль.')
    else:
        form = LoginForm()

    return render(request, 'registration/login.html', {'form': form})


# Выход
def logout_view(request):
    if request.user.is_authenticated:
        username = request.user.username
        logout(request)
        messages.success(request, f'До свидания, {username}! Вы успешно вышли из системы.')
    return redirect('login')