from django.urls import path
from . import views


urlpatterns = [
    path("profile/<int:id>", views.profile, name="profile"),
    path("profile_edit/<int:id>", views.profile_edit, name="profile_edit"),
]
