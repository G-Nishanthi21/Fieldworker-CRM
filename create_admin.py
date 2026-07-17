import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "field_worker.settings")
django.setup()

from accounts.models import User, UserRole

user, created = User.objects.get_or_create(
    username="admin",
    defaults={
        "email": "admin@gmail.com",
    }
)

user.set_password("Admin@12345")
user.is_superuser = True
user.is_staff = True
user.role = UserRole.ADMIN
user.save()

print("Admin ready with ADMIN role")