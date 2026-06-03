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
        ('low',    'Low'),
        ('medium', 'Medium'),
        ('high',   'High'),
    ]

    RECURRENCE_CHOICES = [
        ('none',       'No recurrence'),
        ('daily',      'Every day'),
        ('weekday',    'Every weekday (Mon–Fri)'),
        ('weekly',     'Every week'),
        ('weekday_on', 'Every specific day of week'),
        ('monthly',    'Every month'),
    ]

    WEEKDAY_CHOICES = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]

    user             = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    category         = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')
    title            = models.CharField(max_length=200)
    description      = models.TextField(blank=True)
    priority         = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    completed        = models.BooleanField(default=False)
    due_date         = models.DateField(null=True, blank=True)
    recurrence       = models.CharField(max_length=12, choices=RECURRENCE_CHOICES, default='none')
    recurrence_weekday = models.IntegerField(choices=WEEKDAY_CHOICES, null=True, blank=True,
                                              help_text='Used when recurrence is "Every specific day of week"')
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['completed', '-priority', 'due_date']

    def __str__(self):
        return self.title

    def recurrence_label(self):
        """Human-readable recurrence label including the specific weekday if set."""
        if self.recurrence == 'weekday_on' and self.recurrence_weekday is not None:
            day_name = dict(self.WEEKDAY_CHOICES).get(self.recurrence_weekday, '')
            return f'Every {day_name}'
        return self.get_recurrence_display()

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
        elif self.recurrence == 'weekday_on' and self.recurrence_weekday is not None:
            # Find the next occurrence of the chosen weekday
            next_day = base + timedelta(days=1)
            while next_day.weekday() != self.recurrence_weekday:
                next_day += timedelta(days=1)
            return next_day
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
            recurrence_weekday=self.recurrence_weekday,
            category=self.category,
            due_date=self.next_due_date(),
            completed=False,
        )
