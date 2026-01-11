from django.urls import path
from . import views
from .views import upload_chunks

urlpatterns = [
    path("upload-chunk/", upload_chunks, name="upload_chunk"),
    path("movie/<int:id>/", views.movie, name="movie"),
    path("serie/<int:id>/", views.serie, name="serie"),
]
