from filmes.services.sprites import (
    get_video_duration,
    generate_video_sprites,
    _upload_hls_files,
)
from celery.exceptions import SoftTimeLimitExceeded
import logging, shutil, tempfile, os, math
from celery import shared_task
from datetime import timedelta
import subprocess


logger = logging.getLogger(__name__)


@shared_task(
    name="calculate_video_duration", bind=True, max_retries=3, default_retry_delay=60
)
def calculate_video_duration(self, object_id, model_type):
    from .models import Movies, Episode

    try:
        if model_type == "movie":
            obj = Movies.objects.get(id=object_id)
            file_field = obj.file_movie
        else:
            obj = Episode.objects.get(id=object_id)
            file_field = obj.file_episode

        if not file_field or not file_field.path:
            return

        duration = get_video_duration(file_field.path)

        if duration > 0:
            obj.duration_all = timedelta(seconds=duration)
            obj.save(update_fields=["duration_all"])
            logger.info(f"Duração de {model_type} {object_id} atualizada.")

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
            obj = Movies.objects.get(id=object_id)
            input_path = obj.file_movie.path
        else:
            obj = Episode.objects.get(id=object_id)
            input_path = obj.file_episode.path
    except (Movies.DoesNotExist, Episode.DoesNotExist):
        return

    temp_dir = tempfile.mkdtemp()

    try:
        hls_playlist_name = "playlist.m3u8"
        output_hls_path = os.path.join(temp_dir, hls_playlist_name)

        command = [
            "ffmpeg",
            "-i",
            input_path,
            "-profile:v",
            "baseline",
            "-level",
            "3.0",
            "-s",
            "1280x720",
            "-start_number",
            "0",
            "-hls_time",
            "10",
            "-hls_list_size",
            "0",
            "-f",
            "hls",
            output_hls_path,
        ]

        subprocess.run(command, check=True)

        cloud_hls_path = _upload_hls_files(obj, temp_dir)

        if cloud_hls_path:
            obj.hls_file = cloud_hls_path
            obj.save(update_fields=["hls_file"])
            logger.info(f"HLS enviado para a nuvem com sucesso: {cloud_hls_path}")
        else:
            logger.error("Falha ao fazer upload dos arquivos HLS para a nuvem.")

    except Exception as e:
        logger.exception("Erro crítico no processamento HLS do objeto %s", object_id)
    finally:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


@shared_task(
    name="generate_video_sprites_task", bind=True, soft_time_limit=1800, time_limit=1920
)
def generate_video_sprites_task(self, object_id, model_type):
    from .models import Movies, Episode, VideoSprite

    try:
        if model_type == "movie":
            obj = Movies.objects.get(id=object_id)
            input_path = obj.file_movie.path
            field_name = obj.file_movie.name
        else:
            obj = Episode.objects.get(id=object_id)
            input_path = obj.file_episode.path
            field_name = obj.file_episode.name
    except (Movies.DoesNotExist, Episode.DoesNotExist):
        return

    temp_dir = tempfile.mkdtemp()

    try:
        duration = get_video_duration(input_path)

        if duration <= 0:
            return

        generate_video_sprites(obj, input_path, temp_dir)

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
                movie=obj if model_type == "movie" else None,
                episode=obj if model_type == "episode" else None,
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

            obj.sprite_vtt = relative_vtt_path
            obj.save(update_fields=["sprite_vtt"])
    except SoftTimeLimitExceeded:
        logger.exception(f"Tempo esgotado para gerar sprites de {object_id}")
    except Exception:
        logger.exception(f"Erro inesperado nos sprites de {object_id}")
    finally:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
