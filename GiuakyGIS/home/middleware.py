from django.http import HttpResponseForbidden
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin

class AdminProtectionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the request is for admin area
        if request.path.startswith('/admin/'):
            # Check if user is authenticated
            if not request.user.is_authenticated:
                # Trigger 403 for unauthenticated users
                response = render(request, '403.html', status=403)
                return response
            # Check if user is superuser or staff
            elif not (request.user.is_superuser or request.user.is_staff):
                # Trigger 403 for non-admin users
                response = render(request, '403.html', status=403)
                return response
        
        response = self.get_response(request)
        return response
