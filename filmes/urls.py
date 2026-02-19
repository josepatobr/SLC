from .views import upload_chunks
from django.conf import settings
from django.urls import path
from . import views

urlpatterns = [
    path("upload-chunk/", upload_chunks, name="upload_chunk"),
    path("movie/<int:id>/", views.movie, name="movie"),
]


def normalize_local_s3_url(url: str) -> str:
    if settings.DEBUG and "minio:9000" in url:
        url = url.replace("minio:9000", "localhost:9000")
    return url


def normalize_local_s3_url_to_service(url: str) -> str:
    if settings.DEBUG and "localhost:9000" in url:
        url = url.replace("localhost:9000", "minio:9000")
    return url