from django.shortcuts import redirect
from django.urls import resolve

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get the current path
        path = request.path_info
        
        # Skip authentication for home page and auth-related pages
        public_paths = [
            '/',  # Home
            '/accounts/login/',  # Login
            '/accounts/signup/',  # Signup
            '/accounts/password/reset/',  # Password reset
            '/accounts/google/login/',  # Google login
            # Add any other public paths here
        ]

        # Check if we should enforce authentication
        if not request.user.is_authenticated and path not in public_paths:
            return redirect('account_login')

        response = self.get_response(request)
        return response