from django.contrib import admin
from .models import Movies, Gender
from django.conf import settings
from django.core.files import File
import os
import shutil

admin.site.register(Movies)
admin.site.register(Gender)


def save_model(self, request, obj, form, change):
    guid = form.cleaned_data.get("video") or form.cleaned_data.get("episode_video")

    if guid and isinstance(guid, str):
        temporary_path = os.path.join(settings.MEDIA_ROOT, "temp_chunks", guid)

        if os.path.exists(temporary_path):
            final_path = os.path.join(settings.MEDIA_ROOT, "temp_chunks", f"{guid}.mp4")

        with open(final_path, "wb") as final_file:
            parts = sorted(
                os.listdir(temporary_path), key=lambda x: int(x.split("_")[1])
            )
            for part in parts:
                with open(os.path.join(temporary_path, part), "rb") as f:
                    final_file.write(f.read())

        with open(final_path, "rb") as f:
            field = obj.video if hasattr(obj, "video") else obj.episode_video
            field.save(f"{guid}.mp4", File(f), save=False)
        os.remove(final_path)
        shutil.rmtree(temporary_path)
    super().save_model(request, obj, form, change)
