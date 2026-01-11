from django.urls import path
from . import views

urlpatterns = [
    # Authentication endpoints
    path('register/', views.register_user, name='register'),
    path('token/', views.login_user, name='login'),
    path('users/<int:user_id>/', views.get_user, name='get-user'),
    
    # Task endpoints
    path('tasks/', views.get_tasks, name='list-tasks'),
    path('tasks/create/', views.create_task, name='create-task'),
    path('tasks/<int:task_id>/', views.get_task, name='get-task'),
    path('tasks/<int:task_id>/update/', views.update_task, name='update-task'),
    path('tasks/<int:task_id>/delete/', views.delete_task, name='delete-task'),
]