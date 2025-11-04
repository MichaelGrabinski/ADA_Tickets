import re
from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse


class GlobalLoginRequiredMiddleware:
    """
    Enforce login site-wide (except exempt paths) and send users to
    the Azure AD login with next set to '/'.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        patterns = list(getattr(settings, 'LOGIN_EXEMPT_URLS', []))
        # Always exempt admin and health/static-ish endpoints
        patterns += [r'^admin/']
        self._compiled = [re.compile(p) for p in patterns]

    def __call__(self, request):
        # Allow exempt paths and already-authenticated users
        path = request.path.lstrip('/')
        if request.user.is_authenticated or any(p.match(path) for p in self._compiled):
            return self.get_response(request)

        # Resolve the LOGIN_URL name to a concrete path (e.g. '/ADA/oauth2/login/')
        try:
            login_path = reverse(settings.LOGIN_URL)
        except Exception:
            # Fallback: assume LOGIN_URL is already a usable path
            login_path = settings.LOGIN_URL

        # If we're already on the login path, don't redirect again
        if request.path.startswith(login_path):
            return self.get_response(request)

        # Preserve the original path the user tried to access
        next_param = request.get_full_path()
        return redirect(f"{login_path}?next={next_param}")
