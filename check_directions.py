import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.directions.models import Direction
count = Direction.objects.count()
print(f"Total Directions: {count}")
if count > 0:
    print("Example:", Direction.objects.first().name)
else:
    print("No directions found!")
