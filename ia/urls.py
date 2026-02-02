from django.urls import path
from . import views


urlpatterns = [path("", views.support_ia, name="support_ia")]
