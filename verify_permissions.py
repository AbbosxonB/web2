
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.accounts.models import CustomUser, ModuleAccess
from rest_framework.test import APIRequestFactory
from apps.accounts.views import EmployeeViewSet

def verify_backend():
    print("Starting Backend Verification...")
    
    # 1. Create a dummy admin user if not exists (to bypass auth if needed, or simply test serializer)
    # Actually, let's test the Serializer directly to avoid ViewSet complexity/Auth for now, 
    # or test ViewSet actions if possible. Serializer test is cleaner for unit logic.
    
    from apps.accounts.serializers import CustomUserSerializer
    
    # Test Data
    user_data = {
        'username': 'test_perm_user',
        'first_name': 'Test',
        'last_name': 'User',
        'role': 'teacher',
        'password': 'password123',
        'permissions': [
            {'module': 'dashboard', 'can_view': True, 'can_update': False},
            {'module': 'students', 'can_view': True, 'can_create': True, 'can_delete': False}
        ]
    }
    
    print(f"DTO: {json.dumps(user_data, indent=2)}")

    # Clean up old
    CustomUser.objects.filter(username='test_perm_user').delete()
    
    # 2. Test Creation
    print("\n[TEST] Creating User via Serializer...")
    serializer = CustomUserSerializer(data=user_data)
    if serializer.is_valid():
        user = serializer.save()
        print(f"User created: {user.username} (ID: {user.id})")
        
        # Verify Permissions
        perms = ModuleAccess.objects.filter(user=user)
        print(f"Permissions found: {perms.count()}")
        for p in perms:
            print(f"- {p.module}: view={p.can_view}, create={p.can_create}")
            
        assert perms.count() == 2
        assert perms.get(module='dashboard').can_view == True
        assert perms.get(module='students').can_create == True
        print("SUCCESS: Creation permissions verified.")
    else:
        print("FAILED: Serializer errors:", serializer.errors)
        return

    # 3. Test Update
    print("\n[TEST] Updating User Permissions...")
    update_data = {
        'permissions': [
            {'module': 'dashboard', 'can_view': False, 'can_update': False}, # Changed view to False
            {'module': 'tests', 'can_view': True} # Added new
            # Removed students (should be gone or re-set depending on logic, my logic replaces all)
        ]
    }
    
    serializer = CustomUserSerializer(user, data=update_data, partial=True)
    if serializer.is_valid():
        user = serializer.save()
        
        perms = ModuleAccess.objects.filter(user=user)
        print(f"Permissions after update: {perms.count()}")
        for p in perms:
            print(f"- {p.module}: view={p.can_view}")
            
        assert perms.count() == 2
        assert perms.get(module='dashboard').can_view == False
        assert perms.filter(module='students').exists() == False
        assert perms.filter(module='tests').exists() == True
        print("SUCCESS: Update permissions verified.")
    else:
        print("FAILED: Update errors:", serializer.errors)

if __name__ == '__main__':
    try:
        verify_backend()
    except Exception as e:
        print(f"ERROR: {e}")
