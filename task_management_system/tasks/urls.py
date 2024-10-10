from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('', views.task_list, name='list'),
    path('create/', views.create_task, name='create_task'),
    path('edit/<str:task_id>/', views.edit_task, name='edit_task'),
    path('delete/<str:task_id>/', views.delete_task, name='delete_task'),
]
