from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.utils import timezone
from .models import Task, Category
from .forms import TaskForm, RegisterForm, CategoryForm, ProfileForm


def demo_login(request):
    from django.contrib.auth import authenticate
    if request.method == 'POST':
        user = authenticate(request, username='demo', password='Demo1234!')
        if user:
            login(request, user)
            messages.success(request, 'You are viewing the demo account.')
        else:
            messages.error(request, 'Demo account not available.')
    return redirect('task-list')


def register(request):
    if request.user.is_authenticated:
        return redirect('task-list')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome, {user.username}!')
            return redirect('task-list')
    else:
        form = RegisterForm()
    return render(request, 'tasks/register.html', {'form': form})


@login_required
def task_list(request):
    today = timezone.now().date()

    status   = request.GET.get('status', 'all')
    priority = request.GET.get('priority', 'all')
    category = request.GET.get('category', 'all')
    query    = request.GET.get('q', '').strip()

    tasks = Task.objects.filter(user=request.user).select_related('category')

    if status == 'active':
        tasks = tasks.filter(completed=False)
    elif status == 'completed':
        tasks = tasks.filter(completed=True)
    elif status == 'overdue':
        tasks = tasks.filter(completed=False, due_date__lt=today)
    elif status == 'today':
        tasks = tasks.filter(completed=False, due_date=today)

    if priority != 'all':
        tasks = tasks.filter(priority=priority)

    if category == 'none':
        tasks = tasks.filter(category__isnull=True)
    elif category != 'all':
        tasks = tasks.filter(category__id=category)

    if query:
        tasks = tasks.filter(title__icontains=query)

    # Stats from full set
    all_tasks = Task.objects.filter(user=request.user)
    total     = all_tasks.count()
    completed = all_tasks.filter(completed=True).count()
    pending   = all_tasks.filter(completed=False).count()
    overdue   = all_tasks.filter(completed=False, due_date__lt=today).count()
    due_today = all_tasks.filter(completed=False, due_date=today).count()

    # Priority counts for sidebar
    high_count   = all_tasks.filter(completed=False, priority='high').count()
    medium_count = all_tasks.filter(completed=False, priority='medium').count()
    low_count    = all_tasks.filter(completed=False, priority='low').count()

    # Annotate overdue flag
    for task in tasks:
        task.is_overdue = (
            not task.completed and
            task.due_date is not None and
            task.due_date < today
        )

    categories = Category.objects.filter(user=request.user)

    context = {
        'tasks': tasks,
        'status': status,
        'priority': priority,
        'category': category,
        'query': query,
        'total': total,
        'completed': completed,
        'pending': pending,
        'overdue': overdue,
        'due_today': due_today,
        'high_count': high_count,
        'medium_count': medium_count,
        'low_count': low_count,
        'categories': categories,
        'today': today,
    }
    return render(request, 'tasks/task_list.html', context)


@login_required
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.user, request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            messages.success(request, 'Task created!')
            return redirect('task-list')
    else:
        form = TaskForm(request.user)
    return render(request, 'tasks/task_form.html', {'form': form, 'action': 'Create'})


@login_required
def task_edit(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        form = TaskForm(request.user, request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, 'Task updated!')
            return redirect('task-list')
    else:
        form = TaskForm(request.user, instance=task)
    return render(request, 'tasks/task_form.html', {'form': form, 'action': 'Edit', 'task': task})


@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        task.delete()
        messages.success(request, 'Task deleted.')
        return redirect('task-list')
    return render(request, 'tasks/task_confirm_delete.html', {'task': task})


@login_required
def task_toggle(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    task.completed = not task.completed
    task.save()
    if task.completed and task.recurrence != 'none':
        task.create_next_occurrence()
        messages.success(request, f'✓ Done! Next "{task.title}" scheduled automatically.')
    return redirect('task-list')


@login_required
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    today = timezone.now().date()
    task.is_overdue = (
        not task.completed and
        task.due_date is not None and
        task.due_date < today
    )
    return render(request, 'tasks/task_detail.html', {'task': task})


@login_required
def profile(request):
    user = request.user
    all_tasks = Task.objects.filter(user=user)
    stats = {
        'total':     all_tasks.count(),
        'completed': all_tasks.filter(completed=True).count(),
        'pending':   all_tasks.filter(completed=False).count(),
    }

    profile_form  = ProfileForm(instance=user)
    password_form = PasswordChangeForm(user)

    if request.method == 'POST':
        if 'update_profile' in request.POST:
            profile_form = ProfileForm(request.POST, instance=user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Profile updated!')
                return redirect('profile')

        elif 'change_password' in request.POST:
            password_form = PasswordChangeForm(user, request.POST)
            if password_form.is_valid():
                updated_user = password_form.save()
                update_session_auth_hash(request, updated_user)  # keep logged in
                messages.success(request, 'Password changed!')
                return redirect('profile')

    return render(request, 'tasks/profile.html', {
        'profile_form': profile_form,
        'password_form': password_form,
        'stats': stats,
    })


# ── Category views ────────────────────────────────────────────────────────────

@login_required
def category_list(request):
    categories = Category.objects.filter(user=request.user).annotate(
        task_count=models.Count('tasks')
    )
    form = CategoryForm()
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            cat = form.save(commit=False)
            cat.user = request.user
            cat.save()
            messages.success(request, f'Category "{cat.name}" created!')
            return redirect('category-list')
    return render(request, 'tasks/category_list.html', {'categories': categories, 'form': form})


@login_required
def category_delete(request, pk):
    cat = get_object_or_404(Category, pk=pk, user=request.user)
    if request.method == 'POST':
        cat.delete()
        messages.success(request, 'Category deleted.')
        return redirect('category-list')
    return render(request, 'tasks/category_confirm_delete.html', {'category': cat})


# need models.Count
from django.db import models
