from django.shortcuts import redirect
from django.urls import resolve, Resolver404

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get the current path
        path = request.path_info
        
        # Skip authentication for home page, legal pages, and auth-related pages
        public_paths = [
            '/',  # Home
            '/terms/', # Terms & Conditions
            '/privacy-policy/',
            '/accounts/login/',  # Login
            '/accounts/signup/',  # Signup
            '/accounts/password/reset/',  # Password reset
            '/accounts/google/login/',  # Google login
            # Add any other public paths here
        ]

        # First check if the URL is valid
        try:
            resolve(path)
            # Only redirect if the URL is valid and requires authentication
            if not request.user.is_authenticated and path not in public_paths:
                return redirect('account_login')
        except Resolver404:
            # Let Django handle 404s naturally
            pass

        response = self.get_response(request)
        return response