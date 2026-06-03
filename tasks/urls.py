from django.urls import path
from . import views
from . import api_views

urlpatterns = [
    # ── HTML views ────────────────────────────────────────────────────────────
    path('demo-login/',           views.demo_login,         name='demo-login'),
    path('',                      views.task_list,          name='task-list'),
    path('create/',               views.task_create,        name='task-create'),
    path('<int:pk>/edit/',        views.task_edit,          name='task-edit'),
    path('<int:pk>/delete/',      views.task_delete,        name='task-delete'),
    path('<int:pk>/toggle/',      views.task_toggle,        name='task-toggle'),
    path('register/',             views.register,           name='register'),
    path('<int:pk>/',             views.task_detail,        name='task-detail'),
    path('profile/',              views.profile,            name='profile'),
    path('categories/',           views.category_list,      name='category-list'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category-delete'),

    # ── REST API ──────────────────────────────────────────────────────────────
    path('api/stats/',                   api_views.task_stats_api,                 name='api-task-stats'),
    path('api/tasks/',                   api_views.TaskListCreateAPI.as_view(),    name='api-task-list'),
    path('api/tasks/<int:pk>/',          api_views.TaskDetailAPI.as_view(),        name='api-task-detail'),
    path('api/tasks/<int:pk>/toggle/',   api_views.task_toggle_api,                name='api-task-toggle'),
    path('api/categories/',              api_views.CategoryListCreateAPI.as_view(), name='api-category-list'),
    path('api/categories/<int:pk>/',     api_views.CategoryDetailAPI.as_view(),    name='api-category-detail'),
]
