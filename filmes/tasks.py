from filmes.services.sprites import get_video_duration, generate_video_sprites
from filmes.services.process import process_video_to_hls
from celery.exceptions import SoftTimeLimitExceeded
import logging, shutil, tempfile, os, math
from celery import shared_task
from datetime import timedelta

logger = logging.getLogger(__name__)


@shared_task(
    name="calculate_video_duration", bind=True, max_retries=3, default_retry_delay=60
)
def calculate_video_duration(self, object_id, model_type):
    from .models import Movies, Episode

    try:
        if model_type == "movie":
            movie_details = Movies.objects.get(id=object_id)
            file_field = movie_details.file_movie
        else:
            serie_details = Episode.objects.get(id=object_id)
            file_field = serie_details.file_episode

        if not file_field or not file_field.path:
            return

        duration = get_video_duration(file_field.path)

        if movie_details.duration > 0:
            movie_details.duration_all = timedelta(seconds=duration)
            movie_details.save(update_fields=["duration_all"])
            logger.info(f"Duração de {model_type}: {object_id} atualizada.")
        else: 
            serie_details.duration > 0
            serie_details.duration_all = timedelta(seconds=duration)
            serie_details.save(update_fields=["duration_all"])
            logger.info(f"Duração de {model_type}: {object_id} atualizada.")

    except (Movies.DoesNotExist, Episode.DoesNotExist):
        logger.error(f"{model_type} com ID {object_id} não encontrado.")
    except Exception as e:
        raise self.retry(exc=e)


@shared_task(
    name="process_video_hls_task", bind=True, soft_time_limit=14400, time_limit=14500
)
def process_video_hls_task(self, object_id, model_type):
    from .models import Movies, Episode

    try:
        if model_type == "movie":
            movie_details = Movies.objects.get(id=object_id)
        else:
            serie_details = Episode.objects.get(id=object_id)
    except (Movies.DoesNotExist, Episode.DoesNotExist):
        return logger.error("Arquivos não existe")

    temp_dir = tempfile.mkdtemp()

    try:
        process_video_to_hls(Movies, Episode, temp_dir)

    except SoftTimeLimitExceeded as e:
        logger.exception("SoftTimeLimitExceeded for video %s", movie_details.id, serie_details.id, exc_info=e)
        shutil.rmtree(temp_dir, ignore_errors=True)
    except Exception as e:
        logger.exception("Unexpected error processing video %s", movie_details.id, serie_details.id, exc_info=e)
        shutil.rmtree(temp_dir, ignore_errors=True)


@shared_task(
    name="generate_video_sprites_task", bind=True, soft_time_limit=1800, time_limit=1920
)
def generate_video_sprites_task(self, object_id, model_type):
    from .models import Movies, Episode, VideoSprite
    
    instance = None

    try:
        if model_type == "movie":
            instance = Movies.objects.get(id=object_id)
            input_path = instance.file_movie.path
            field_name = instance.file_movie.name
        else:
            instance = Episode.objects.get(id=object_id)
            input_path = instance.file_episode.path
            field_name = instance.file_episode.name
    except (Movies.DoesNotExist, Episode.DoesNotExist):
        return

    temp_dir = tempfile.mkdtemp()

    try:
        duration = get_video_duration(input_path)

        if duration <= 0:
            return

        generate_video_sprites(instance, input_path, temp_dir)

        final_dir = os.path.join(os.path.dirname(input_path), "sprites")
        os.makedirs(final_dir, exist_ok=True)

        for filename in os.listdir(temp_dir):
            shutil.move(
                os.path.join(temp_dir, filename), os.path.join(final_dir, filename)
            )

            field_dir = os.path.dirname(field_name)
            relative_image_path = os.path.join(
                field_dir, "sprites", "sprite.jpg"
            ).replace("\\", "/")
            relative_vtt_path = os.path.join(
                field_dir, "sprites", "thumbnails.vtt"
            ).replace("\\", "/")

            VideoSprite.objects.update_or_create(
                movie=instance if model_type == "movie" else None,
                episode=instance if model_type == "episode" else None,
                defaults={
                    "start_time": 0,
                    "end_time": duration,
                    "interval": 10,
                    "columns": 5,
                    "rows": math.ceil((duration / 10) / 5),
                    "frame_width": 160,
                    "image": relative_image_path,
                },
            )
            instance.sprite_vtt = relative_vtt_path
            instance.save(update_fields=["sprite_vtt"])
    except SoftTimeLimitExceeded:
        logger.exception(f"Tempo esgotado para gerar sprites de {object_id}")
    except Exception:
        logger.exception(f"Erro inesperado nos sprites de {object_id}")
    finally:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)


