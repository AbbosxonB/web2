from django.utils import timezone
from datetime import timedelta

class ActivityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            now = timezone.now()
            # Optimization: Only update if last_activity is None or older than 1 minute
            # This prevents writing to DB on every single request (static files, polling, etc.)
            last_activity = getattr(request.user, 'last_activity', None)
            
            should_update = False
            if last_activity is None:
                should_update = True
            elif now - last_activity > timedelta(minutes=1):
                should_update = True
            
            if should_update:
                request.user.last_activity = now
                request.user.save(update_fields=['last_activity'])

        response = self.get_response(request)
        return response
