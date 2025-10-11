from ninja.security import HttpBearer
from rest_framework_simplejwt.authentication import JWTAuthentication

class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        validated = JWTAuthentication().authenticate(request)
        if validated:
            return validated[0] 