from django.contrib.auth import get_user_model
from django.contrib import auth
from django.conf import settings

User = get_user_model()


class AutoLoginMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if settings.DEBUG and not request.user.is_authenticated:
            user = User.objects.filter(is_superuser=True).first()
            if user:
                auth.login(
                    request, user, backend="django.contrib.auth.backends.ModelBackend"
                )

        return self.get_response(request)
