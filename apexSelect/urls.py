from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Аутентификация
    path('', views.home_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Управление вакансиями
    path('vacancies/', views.vacancy_list_view, name='vacancy_list'),
    path('vacancies/add/', views.add_vacancy_view, name='add_vacancy'),
    path('vacancies/<int:pk>/', views.vacancy_detail_view, name='vacancy_detail'),
    path('vacancies/<int:pk>/edit/', views.edit_vacancy_view, name='edit_vacancy'),
    path('vacancies/<int:pk>/delete/', views.delete_vacancy_view, name='delete_vacancy'),
    path('vacancies/<int:pk>/toggle-status/', views.toggle_vacancy_status, name='toggle_vacancy_status'),

    # Отклики на вакансии
    path('vacancies/<int:pk>/respond/', views.respond_to_vacancy_view, name='respond_vacancy'),
    path('my-responses/', views.my_responses_view, name='my_responses'),
    path('responses/<int:pk>/delete/', views.delete_response_view, name='delete_response'),
    path('vacancies/<int:pk>/responses/', views.vacancy_responses_view, name='vacancy_responses'),
    path('responses/<int:pk>/update-status/', views.update_response_status_view, name='update_response_status'),
]

# Обработчики для сброса пароля (опционально)
urlpatterns += [
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='registration/password_reset.html',
             email_template_name='registration/password_reset_email.html',
             subject_template_name='registration/password_reset_subject.txt',
             success_url='/password-reset/done/'
         ),
         name='password_reset'),

    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='registration/password_reset_done.html'
         ),
         name='password_reset_done'),

    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='registration/password_reset_confirm.html',
             success_url='/reset/done/'
         ),
         name='password_reset_confirm'),

    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='registration/password_reset_complete.html'
         ),
         name='password_reset_complete'),
]