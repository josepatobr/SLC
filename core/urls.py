from django.contrib import admin
from django.urls import path, include
from core.api import api
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
    path("auth/", include("cadastro.urls")),
    path("", include("home.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
