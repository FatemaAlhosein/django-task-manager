#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate

# Load initial data only if no users exist yet
python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.exists():
    from django.core.management import call_command
    call_command('loaddata', 'tasks/fixtures/initial_data.json')
    print('Fixture loaded.')
else:
    print('Data already exists, skipping fixture.')
"
