from django.contrib.auth import logout
from django.utils import timezone
from django.shortcuts import redirect
from django.urls import reverse

class SessionTimeoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            last_activity = request.session.get('last_activity')
            if last_activity:
                inactive_time = timezone.now() - timezone.datetime.fromisoformat(last_activity)
                if inactive_time.total_seconds() > 1800:
                    logout(request)
                    return redirect(reverse('authentication:login')) 
            
            request.session['last_activity'] = timezone.now().isoformat()

        response = self.get_response(request)
        return response