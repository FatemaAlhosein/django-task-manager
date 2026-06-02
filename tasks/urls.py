from django.urls import path
from . import views

urlpatterns = [
    path('',                      views.task_list,          name='task-list'),
    path('create/',               views.task_create,        name='task-create'),
    path('<int:pk>/edit/',        views.task_edit,          name='task-edit'),
    path('<int:pk>/delete/',      views.task_delete,        name='task-delete'),
    path('<int:pk>/toggle/',      views.task_toggle,        name='task-toggle'),
    path('register/',             views.register,           name='register'),
    path('categories/',           views.category_list,      name='category-list'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category-delete'),
]
