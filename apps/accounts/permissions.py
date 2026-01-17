from rest_framework import permissions

class IsStudentGroupActive(permissions.BasePermission):
    """
    Global permission check for blocking students if their group is inactive.
    """
    message = 'Sizning guruhingiz tizimga kirishiga ruxsat berilmagan. Dekanatga murojaat qiling!'

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return True # Allow anonymous (auth handled elsewhere) or unauthenticated

        if request.user.role == 'student':
            student_profile = getattr(request.user, 'student_profile', None)
            if student_profile and student_profile.group and not student_profile.group.is_system_active:
                return False
        
        return True
