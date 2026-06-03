from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from tasks.models import Task, Category
from django.utils import timezone


class Command(BaseCommand):
    help = 'Creates demo user with sample tasks'

    def handle(self, *args, **kwargs):
        if User.objects.filter(username='demo').exists():
            self.stdout.write('Demo user already exists.')
            return

        user = User.objects.create_user(
            username='demo',
            password='Demo1234!',
            first_name='Demo',
        )

        today = timezone.now().date()

        # Categories
        work     = Category.objects.create(user=user, name='Work',     color='#4f86c6')
        home     = Category.objects.create(user=user, name='Home',     color='#e06c75')
        personal = Category.objects.create(user=user, name='Personal', color='#e5c07b')
        family   = Category.objects.create(user=user, name='Family',   color='#98c379')

        # Tasks
        tasks = [
            dict(title='Pick up kids from school',     category=family,   priority='high',   recurrence='weekday', due_date=today),
            dict(title='Cook dinner',                  category=home,     priority='high',   recurrence='daily',   due_date=today,   description='Ready at 6:00 pm'),
            dict(title='Prepare breakfast for kids',   category=family,   priority='high',   recurrence='daily',   due_date=today),
            dict(title='Clean kitchen',                category=home,     priority='medium', recurrence='daily',   due_date=today,   description='Wash dishes and wipe surfaces'),
            dict(title='Laundry',                      category=home,     priority='medium', recurrence='weekly',  due_date=today,   description='Wash and fold clothes'),
            dict(title='Grocery shopping',             category=home,     priority='high',   recurrence='weekly',  due_date=today),
            dict(title='Pay bills',                    category=None,     priority='high',   recurrence='monthly', due_date=today,   description='Electricity, internet, rent'),
            dict(title='Help kids with homework',      category=family,   priority='high',   recurrence='daily',   due_date=today,   description='Check school work and assignments'),
            dict(title='Practice React',               category=personal, priority='medium', recurrence='daily',   due_date=today,   description='Build small components and practice hooks'),
            dict(title='Work on portfolio project',    category=personal, priority='medium', recurrence='weekly',  due_date=today,   description='Improve task manager app or add new features'),
            dict(title='Watch coding tutorial',        category=personal, priority='medium', recurrence='weekday', due_date=today,   description='Follow a YouTube or course lesson'),
            dict(title='Read documentation',           category=personal, priority='medium', recurrence='daily',   due_date=today,   description='Read Django or React official docs'),
            dict(title='Doctor appointment for child', category=family,   priority='high',   recurrence='none',    due_date=today),
            dict(title='Organize kids clothes',        category=home,     priority='low',    recurrence='none',    due_date=today,   description='Sort old and new clothes'),
            dict(title='Team meeting',                 category=work,     priority='high',   recurrence='weekly',  due_date=today,   description='Weekly sync with team'),
        ]

        for t in tasks:
            Task.objects.create(user=user, **t)

        self.stdout.write(self.style.SUCCESS(f'Demo user created with {len(tasks)} tasks.'))
