import os
import django
from django.test import Client
from django.contrib.auth import get_user_model

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

User = get_user_model()
client = Client()

# Create or get an admin user for testing
username = 'test_admin_results'
password = 'test_password'
if not User.objects.filter(username=username).exists():
    user = User.objects.create_superuser(username=username, password=password, role='admin')
else:
    user = User.objects.get(username=username)

# Login
login_success = client.login(username=username, password=password)
if not login_success:
    print("Login failed")
    exit(1)

# Get Token (Simulating DRF token auth if needed, but Client Session Auth works for some views if SessionAuth is enabled. 
# DRF settings: DEFAULT_AUTHENTICATION_CLASSES include JWT. 
# We need to get a token manually to test JWT auth, OR rely on SessionAuth if enabled. 
# Settings only showed JWT. So Client login might not work for API views depending on views setup.)

# Let's try to get a token pair first using the API
response = client.post('/api/token/', {'username': username, 'password': password})
if response.status_code == 200:
    token = response.json()['access']
    print("Got Token. Testing API...")
    
    # Test Results API
    response = client.get('/api/results/', HTTP_AUTHORIZATION=f'Bearer {token}')
    print(f"Results API Status: {response.status_code}")
    if response.status_code != 200:
        print(f"Error Content: {response.content.decode()}")
    else:
        print("Results API Success")
        print(response.json())
else:
    print(f"Token fetch failed: {response.status_code}")
    print(response.content.decode())
