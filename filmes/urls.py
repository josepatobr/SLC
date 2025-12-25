from django.urls import path
from .views import upload_chunks

urlpatterns = [
    path("upload-chunk/", upload_chunks, name="upload_chunk"),
]
