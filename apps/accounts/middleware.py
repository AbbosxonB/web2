from django.utils import timezone
from datetime import timedelta

class ActivityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            try:
                now = timezone.now()
                # Use simplified logic to avoid potential type errors
                last_activity = getattr(request.user, 'last_activity', None)
                
                should_update = False
                if not last_activity:
                     should_update = True
                else:
                    # Ensure last_activity is comparable
                    try:
                        if now - last_activity > timedelta(minutes=1):
                            should_update = True
                    except (TypeError, ValueError):
                        should_update = True # Force update if comparison fails
                
                if should_update:
                    request.user.last_activity = now
                    request.user.save(update_fields=['last_activity'])
            except Exception as e:
                # Log error but do NOT crash the request
                print(f"MIDDLEWARE ERROR: {str(e)}")
                pass

        response = self.get_response(request)
        return response
