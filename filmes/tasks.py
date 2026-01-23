from filmes.services.sprites import (
    process_video_to_hls,
    get_video_duration,
    generate_video_sprites,
    get_video_tracks_metadata,
)
from celery.exceptions import SoftTimeLimitExceeded
from .models import Video, VideoTrack
import logging, shutil, tempfile
from celery import shared_task
from pathlib import Path


logger = logging.getLogger(__name__)


@shared_task(
    name="calculate_video_duration", bind=True, max_retries=3, default_retry_delay=60
)
def calculate_video_duration(self, video_id):
    try:
        video = Video.objects.get(id=video_id)
        if not video.source_file or not video.source_file.url:
            logger.warning(f"Vídeo {video_id} não possui arquivo de origem.")
            return

        duration = get_video_duration(video.source_file.url)

        if duration > 0:
            video.duration = duration
            video.save(update_fields=["duration"])
            logger.info(f"Duração do vídeo {video_id} atualizada para {duration}s")
        else:
            logger.error(f"Não foi possível calcular a duração para o vídeo {video_id}")
    except Video.DoesNotExist:
        logger.error(f"Vídeo com ID {video_id} não existe no banco de dados.")
    except Exception as e:
        logger.exception(f"Erro ao processar vídeo {video_id}")
        raise self.retry(exc=e)


@shared_task(name="process_video_hls_task", soft_time_limit=14400, time_limit=14500)
def process_video_hls_task(self, video_id):
    try:
        video = Video.objects.get(id=video_id)
    except Video.DoesNotExist as e:
        logger.exception("Video with ID %s does not exist", video_id, exc_info=e)
        return

    temp_dir = tempfile.mkdtemp()
    try:
        process_video_to_hls(video, temp_dir)
        discover_tracks_task.delay(video_id)
    except SoftTimeLimitExceeded as e:
        logger.exception("SoftTimeLimitExceeded for video %s", video_id, exc_info=e)
        shutil.rmtree(temp_dir, ignore_errors=True)
        video.status = Video.Status.FAILED
        video.processing_error = f"SoftTimeLimitExceeded: {e}"
        video.save(update_fields=["status", "processing_error"])
    except Exception as e:
        logger.exception("Unexpected error processing video %s", video_id, exc_info=e)
        shutil.rmtree(temp_dir, ignore_errors=True)
        video.status = Video.Status.FAILED
        video.processing_error = str(e)
        video.save(update_fields=["status", "processing_error"])


@shared_task(name="generate_video_sprites_task", soft_time_limit=1800, time_limit=1920)
def generate_video_sprites_task(self, video_id):
    try:
        video = Video.objects.get(id=video_id)
    except Video.DoesNotExist as e:
        logger.exception("Video with ID %s does not exist", video_id, exc_info=e)
        return

    temp_dir = tempfile.mkdtemp()
    try:
        generate_video_sprites(video, temp_dir)
    except SoftTimeLimitExceeded as e:
        logger.exception("SoftTimeLimitExceeded for video %s", video_id, exc_info=e)
        shutil.rmtree(temp_dir, ignore_errors=True)
        video.status = Video.Status.FAILED
        video.processing_error = f"SoftTimeLimitExceeded: {e}"
        video.save(update_fields=["status", "processing_error"])
    except Exception as e:
        logger.exception("Unexpected error processing video %s", video_id, exc_info=e)
        shutil.rmtree(temp_dir, ignore_errors=True)
        video.status = Video.Status.FAILED
        video.processing_error = str(e)
        video.save(update_fields=["status", "processing_error"])


@shared_task(name="discover_tracks_task")
def discover_tracks_task(self, video_id):
    try:
        video = Video.objects.get(id=video_id)
    except Video.DoesNotExist as e:
        logger.exception("Video with ID %s does not exist", video_id, exc_info=e)
        return

    metadata = get_video_tracks_metadata(video.source_file.url)
    if not metadata:
        return

    for stream in metadata["audio"]:
        track, created = VideoTrack.objects.update_or_create(
            video=video,
            language=stream["language"],
            defaults={
                "source_audio_index": stream["index"],
                "label": stream["label"],
            },
        )
        if created or not track.audio_playlist:
            process_track_task.delay(track.id)

    for stream in metadata["subtitle"]:
        track, created = VideoTrack.objects.update_or_create(
            video=video,
            language=stream["language"],
            defaults={
                "source_subtitle_index": stream["index"],
                "label": stream["label"],
            },
        )
        if created or not track.subtitle_file:
            process_track_task.delay(track.id)


@shared_task(name="process_track_task", soft_time_limit=3600, time_limit=3700)
def process_track_task(self, track_id):
    try:
        track = VideoTrack.objects.select_related("video").get(id=track_id)
    except VideoTrack.DoesNotExist:
        return

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
