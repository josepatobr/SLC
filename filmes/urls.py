from .views import upload_chunks
from django.urls import path
from . import views

urlpatterns = [
    path("upload-chunk/", upload_chunks, name="upload_chunk"),
    path("movie/<int:id>/", views.movie, name="movie"),
]
