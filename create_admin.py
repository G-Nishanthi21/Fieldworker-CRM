import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "field_worker.settings")
django.setup()

from accounts.models import User

if not User.objects.filter(username="admin").exists():
    User.objects.create_superuser(
        username="admin",
        email="admin@gmail.com",
        password="Admin@12345"
    )
    print("Admin created")
else:
    print("Admin already exists")