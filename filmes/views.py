from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib import messages
from django.conf import settings
from .models import Video
import os


@csrf_exempt
def upload_chunks(request):
    get_file = request.FILES.get("file")
    file_guide = request.POST.get("dzuuid")
    chunk_index = int(request.POST.get("dzchunkindex", 0))
    all_chunks = int(request.POST.get("dztotalchunkcount", 1))

    temporary_path = os.path.join(settings.MEDIA_ROOT, "temp_chunks", file_guide)
    os.makedirs(temporary_path, exist_ok=True)

    with open(os.path.join(temporary_path, f"part_{chunk_index}"), "wb") as f:
        for chunk in get_file.chunks():
            f.write(chunk)

    if chunk_index + 1 == all_chunks:
        return JsonResponse({"status": "complete", "guid": file_guide})
    return JsonResponse({"status": "uploading"})


@login_required
def movie(request, id):
    user = request.user
    if user.user_status == "user_comum":
        messages.error(request, "Você precisa ser vip para acessar essa area.")
        return redirect("home")

    movie = get_object_or_404(Video, id=id)

    return render(
        request,
        "movie.html",
        {
            "movie": movie,
        },
    )
