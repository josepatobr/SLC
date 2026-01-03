from django.urls import path
from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("movie/<int:id>/", views.movie, name="movie"),
    path("serie/<int:id>/", views.serie, name="serie"),
    path("profile/<int:id>", views.profile, name="profile"),
]
