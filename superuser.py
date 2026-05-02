import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TglabTest.settings')

django.setup()

from config import get_config
from users.models import User

config = get_config()

if not User.objects.filter(name=config.django.admin_name).exists():
    User.objects.create_superuser(
        config.django.admin_name,
        config.django.admin_email,
        config.django.admin_password
    )
    print(f"Superuser {config.django.admin_name} created.")
else:
    print("Superuser already exists.")