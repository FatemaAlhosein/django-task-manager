from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from dateutil.relativedelta import relativedelta


class Task(models.Model):
    PRIORITY_CHOICES = [
        ('low',    'Low'),
        ('medium', 'Medium'),
        ('high',   'High'),
    ]

    RECURRENCE_CHOICES = [
        ('none',    'No recurrence'),
        ('daily',   'Every day'),
        ('weekly',  'Every week'),
        ('monthly', 'Every month'),
    ]

    user        = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
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
        """Calculate the next due date based on recurrence."""
        base = self.due_date or timezone.now().date()
        if self.recurrence == 'daily':
            return base + timedelta(days=1)
        elif self.recurrence == 'weekly':
            return base + timedelta(weeks=1)
        elif self.recurrence == 'monthly':
            return base + relativedelta(months=1)
        return None

    def create_next_occurrence(self):
        """Create the next recurring task when this one is completed."""
        if self.recurrence == 'none':
            return None
        next_date = self.next_due_date()
        return Task.objects.create(
            user=self.user,
            title=self.title,
            description=self.description,
            priority=self.priority,
            recurrence=self.recurrence,
            due_date=next_date,
            completed=False,
        )
