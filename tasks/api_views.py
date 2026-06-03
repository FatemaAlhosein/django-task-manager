from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Task, Category
from .serializers import TaskSerializer, CategorySerializer


# ── Categories ────────────────────────────────────────────────────────────────

class CategoryListCreateAPI(generics.ListCreateAPIView):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CategoryDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)


# ── Tasks ─────────────────────────────────────────────────────────────────────

class TaskListCreateAPI(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Task.objects.filter(user=self.request.user).select_related('category')

        # Filters
        status   = self.request.query_params.get('status')
        priority = self.request.query_params.get('priority')
        category = self.request.query_params.get('category')
        q        = self.request.query_params.get('q', '').strip()

        from django.utils import timezone
        today = timezone.now().date()

        if status == 'active':
            qs = qs.filter(completed=False)
        elif status == 'completed':
            qs = qs.filter(completed=True)
        elif status == 'overdue':
            qs = qs.filter(completed=False, due_date__lt=today)
        elif status == 'today':
            qs = qs.filter(completed=False, due_date=today)

        if priority and priority != 'all':
            qs = qs.filter(priority=priority)

        if category and category != 'all':
            qs = qs.filter(category__id=category)

        if q:
            qs = qs.filter(title__icontains=q)

        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_context(self):
        return {'request': self.request}


class TaskDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

    def get_serializer_context(self):
        return {'request': self.request}


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def task_toggle_api(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    task.completed = not task.completed
    task.save()
    if task.completed and task.recurrence != 'none':
        task.create_next_occurrence()
    serializer = TaskSerializer(task, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def task_stats_api(request):
    from django.utils import timezone
    today = timezone.now().date()
    all_tasks = Task.objects.filter(user=request.user)
    return Response({
        'total':        all_tasks.count(),
        'completed':    all_tasks.filter(completed=True).count(),
        'pending':      all_tasks.filter(completed=False).count(),
        'overdue':      all_tasks.filter(completed=False, due_date__lt=today).count(),
        'due_today':    all_tasks.filter(completed=False, due_date=today).count(),
        'high_count':   all_tasks.filter(completed=False, priority='high').count(),
        'medium_count': all_tasks.filter(completed=False, priority='medium').count(),
        'low_count':    all_tasks.filter(completed=False, priority='low').count(),
    })
