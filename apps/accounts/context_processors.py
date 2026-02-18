from .models import ModuleAccess

def user_permissions(request):
    """
    Context processor to add granular permissions to the template context.
    Returns 'user_perms' dictionary.
    """
    if not request.user.is_authenticated:
        return {'user_perms': {}}

    # If admin, give full access implicitly (or handle in template)
    # But for sidebar consistency, let's just use the strict ModuleAccess for non-admins
    # and maybe a flag for admins.
    
    # Actually, the sidebar currently shows everything for non-students.
    # We want to restrict it based on ModuleAccess.
    
    perms = {}
    
    # Pre-populate with False defaults for critical modules to avoid KeyError if using lookups
    # (though in templates {{ user_perms.key }} returns None/Falsey if missing, so it's fine)
    
    if request.user.role == 'admin':
        # Admin sees everything
        return {'user_perms': {'is_admin': True}}

    # Fetch permissions
    access_list = ModuleAccess.objects.filter(user=request.user)
    
    for access in access_list:
        # Format: can_view_dashboard, can_view_results, etc.
        perms[f"can_view_{access.module}"] = access.can_view
        perms[f"can_create_{access.module}"] = access.can_create
        perms[f"can_update_{access.module}"] = access.can_update
        perms[f"can_delete_{access.module}"] = access.can_delete
        perms[f"can_export_{access.module}"] = access.can_export

    return {'user_perms': perms}
