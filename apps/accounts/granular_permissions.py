from rest_framework import permissions
from .models import ModuleAccess

class GranularPermission(permissions.BasePermission):
    """
    Checks ModuleAccess for specific actions.
    Map HTTP methods to actions:
    GET -> view
    POST -> create
    PUT/PATCH -> update
    DELETE -> delete
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
            
        # Admin overrides
        if request.user.role == 'admin':
            return True
            
        # Determine module name from viewset (needs 'module_name' attribute or map)
        module = getattr(view, 'module_name', None)
        if not module:
            return True # Fallback if not module-protected
            
        # Map method to permission field
        method_map = {
            'GET': 'can_view',
            'POST': 'can_create',
            'PUT': 'can_update',
            'PATCH': 'can_update',
            'DELETE': 'can_delete'
        }
        
        required_perm = method_map.get(request.method)
        if not required_perm:
            return True
            
        # Check permission
        has_perm = ModuleAccess.objects.filter(
            user=request.user, 
            module=module, 
            **{required_perm: True}
        ).exists()

        if not has_perm:
            from rest_framework.exceptions import PermissionDenied
            action_names = {
                'can_view': "ko'rish",
                'can_create': "yaratish",
                'can_update': "tahrirlash",
                'can_delete': "o'chirish"
            }
            action_text = action_names.get(required_perm, 'bajarish')
            raise PermissionDenied(f"Siz {action_text} amalini bajara olmaysiz.")
            
        return True
