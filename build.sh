#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate

# Load tasks/categories only if no tasks exist yet
python manage.py shell -c "
from tasks.models import Task
if not Task.objects.exists():
    from django.core.management import call_command
    call_command('loaddata', 'tasks/fixtures/initial_data.json')
    print('Fixture loaded.')
else:
    print('Tasks already exist, skipping fixture.')
"
