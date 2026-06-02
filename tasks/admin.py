from django.contrib import admin
from .models import Task, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'color']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display  = ['title', 'user', 'category', 'priority', 'completed', 'due_date', 'recurrence']
    list_filter   = ['completed', 'priority', 'category', 'user']
    search_fields = ['title', 'description']
