import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bavaria_attendance.settings')
django.setup()

from apps.accounts.models import User

if not User.objects.filter(username='admin').exists():
    user = User.objects.create_superuser(
        username='admin',
        email='admin@bavaria.com',
        password='admin123',
        role='admin'
    )
    print('Superuser created: admin / admin123')
else:
    print('Admin user already exists')
