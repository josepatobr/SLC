from allauth.account.decorators import secure_admin_login
from django.conf.urls.static import static
from django.urls import path, include
from django.conf import settings
from django.contrib import admin
from .api import api


(admin.autodiscover(),)
admin.site.login = secure_admin_login(admin.site.login)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
    path("", include("home.urls")),
    path("chat/", include("ia.urls")),
    path("users/", include("users.urls")),
    path("accounts/", include("allauth.urls")),
    path("checkout/", include("payment.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
