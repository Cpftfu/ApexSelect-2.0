from django.urls import path
from . import views

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
]