from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from dateutil.relativedelta import relativedelta


class Category(models.Model):
    COLOR_CHOICES = [
        ('#4f86c6', 'Blue'),
        ('#e06c75', 'Red'),
        ('#98c379', 'Green'),
        ('#e5c07b', 'Yellow'),
        ('#c678dd', 'Purple'),
        ('#56b6c2', 'Teal'),
        ('#d19a66', 'Orange'),
    ]

    user  = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories')
    name  = models.CharField(max_length=50)
    color = models.CharField(max_length=10, choices=COLOR_CHOICES, default='#4f86c6')

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name


class Task(models.Model):
    PRIORITY_CHOICES = [
        ('low',     'Low'),
        ('medium',  'Medium'),
        ('high',    'High'),
    ]

    RECURRENCE_CHOICES = [
        ('none',    'No recurrence'),
        ('daily',   'Every day'),
        ('weekday', 'Every weekday'),
        ('weekly',  'Every week'),
        ('monthly', 'Every month'),
    ]

    user        = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    category    = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')
    title       = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    priority    = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    completed   = models.BooleanField(default=False)
    due_date    = models.DateField(null=True, blank=True)
    recurrence  = models.CharField(max_length=10, choices=RECURRENCE_CHOICES, default='none')
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['completed', '-priority', 'due_date']

    def __str__(self):
        return self.title

    def next_due_date(self):
        base = self.due_date or timezone.now().date()
        if self.recurrence == 'daily':
            return base + timedelta(days=1)
        elif self.recurrence == 'weekday':
            next_day = base + timedelta(days=1)
            while next_day.weekday() >= 5:
                next_day += timedelta(days=1)
            return next_day
        elif self.recurrence == 'weekly':
            return base + timedelta(weeks=1)
        elif self.recurrence == 'monthly':
            return base + relativedelta(months=1)
        return None

    def create_next_occurrence(self):
        if self.recurrence == 'none':
            return None
        return Task.objects.create(
            user=self.user,
            title=self.title,
            description=self.description,
            priority=self.priority,
            recurrence=self.recurrence,
            category=self.category,
            due_date=self.next_due_date(),
            completed=False,
        )
