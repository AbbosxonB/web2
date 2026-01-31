from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, ModuleAccess

@receiver(post_save, sender=CustomUser)
def create_default_permissions(sender, instance, created, **kwargs):
    """
    Assign default permissions to new users if they don't have any accesses yet.
    This ensures that users created via Admin or Shell have at least some basic access.
    """
    if created and not instance.module_accesses.exists():
        role = instance.role
        
        # Define default permissions per role
        # Format: 'module': {'can_view': True, ...}
        defaults = {}
        
        if role == 'dean':
            for mod in ['dashboard', 'groups', 'students', 'results', 'directions', 'subjects', 'tests', 'employees']:
                defaults[mod] = {'can_view': True, 'can_create': True, 'can_update': True, 'can_delete': True, 'can_export': True}
                
        elif role == 'teacher':
             # View access
            for mod in ['dashboard', 'groups', 'students', 'subjects', 'tests', 'results']:
                defaults[mod] = {'can_view': True}
            
            # Create/Edit access for own tests/results (logically)
            defaults['tests']['can_create'] = True
            defaults['tests']['can_update'] = True
            defaults['results']['can_create'] = True # Maybe manual result entry?
            defaults['results']['can_update'] = True
            
        elif role == 'student':
            defaults['tests'] = {'can_view': True}
            defaults['results'] = {'can_view': True}
            
        # Create records
        for module, perms in defaults.items():
            ModuleAccess.objects.create(
                user=instance, 
                module=module,
                **perms
            )
