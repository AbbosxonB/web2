import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.urls import resolve, reverse

try:
    match = resolve('/take/1/')
    print(f"Resolved: {match.func.__name__} (url_name: {match.url_name})")
except Exception as e:
    print(f"Resolution failed: {e}")

try:
    match = resolve('/tests/take/1/')
    print(f"Resolved: {match.func.__name__} (url_name: {match.url_name})")
except Exception as e:
    print(f"Resolution failed: {e}")
