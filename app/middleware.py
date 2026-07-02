from django.shortcuts import redirect
from django.conf import settings
from django.urls import reverse_lazy, resolve, Resolver404

class LoginRequiredMiddleware:
    EXEMPT_URL_NAMES = [
        'login:login',
        'login:logout',
    ]

    def __init__(self, get_response):
        self.get_response = get_response
        self.exempt_urls = [
            str(reverse_lazy(name)) for name in self.EXEMPT_URL_NAMES
        ]

    def __call__(self, request):
        if not request.user.is_authenticated:
            path = request.path_info
            if not any(path.startswith(url) for url in self.exempt_urls):
                login_url = str(reverse_lazy(settings.LOGIN_URL))
                return redirect(f'{login_url}?next={path}')
        return self.get_response(request)