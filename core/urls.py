from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .api import api
from django.contrib import admin
from allauth.account.decorators import secure_admin_login

admin.autodiscover(),
admin.site.login = secure_admin_login(admin.site.login)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
    path("", include("home.urls")),
    path('accounts/', include('allauth.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
