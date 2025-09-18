import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "purple_desk.settings")
django.setup()

from myapp.models import User

u = User.objects.get(username="admin")  # replace with your superuser name
u.is_active = True
u.save()
print("Superuser activated ✅")
