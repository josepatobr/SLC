from django.db.models.signals import post_save
from django.dispatch import receiver
from filmes.models import Serie, Movies
from .views import resize_and_save_poster
import os


@receiver(post_save, sender=(Serie, Movies))
def generate_responsive_posters(sender, instance, created, **kwargs):
    if not created:
        return

    poster_field = None

    if sender == Serie and hasattr(instance, "serie_poster") and instance.serie_poster:
        poster_field = instance.serie_poster

    elif sender == Movies and hasattr(instance, "poster") and instance.poster:
        poster_field = instance.poster

    if not poster_field:
        return
    try:
        original_path = poster_field.path
        output_dir = os.path.dirname(original_path)
        base_name = f"{sender.__name__}-{instance.pk}"

        paths = resize_and_save_poster(original_path, base_name, output_dir)
    except Exception as e:
        print(f"Erro ao processar imagem para {sender.__name__} {instance.pk}: {e}")
        return

    if paths:
        media_path = os.path.dirname(poster_field.url)

        instance.poster_400w = os.path.join(media_path, paths.get("400w", ""))
        instance.poster_800w = os.path.join(media_path, paths.get("800w", ""))
        instance.poster_1200w = os.path.join(media_path, paths.get("1200w", ""))

        instance.save(update_fields=["poster_400w", "poster_800w", "poster_1200w"])

        print(
            f"Sucesso: Pôsteres responsivos gerados e salvos para {sender.__name__} {instance.pk}"
        )
