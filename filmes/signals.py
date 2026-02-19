from .tasks import calculate_video_duration, generate_video_sprites_task, process_video_hls_task
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Movies, Episode
from django.db import transaction
import logging


logger = logging.getLogger(__name__)


@receiver(post_save, sender=Movies)
def movie_post_save(sender, instance, created, **kwargs):
    if not instance.file_movie:
        logger.error("arquivo não encontrado")
        print("mensagem 1")
        return

    if created or not instance.duration_all:
        transaction.on_commit(
            lambda: calculate_video_duration.delay(instance.id, "movie")
        )
    else:
        logger.error("erro na hora da criação")
        print("mensagem 2")
        return

    if not instance.hls_file:
        transaction.on_commit(
            lambda: process_video_hls_task.delay(instance.id, "movie")
        )
    else: 
        logger.error("erro ao processar para hls")
        print("mensagem 3")
        return

    if not instance.sprite_vtt:
        transaction.on_commit(
            lambda: generate_video_sprites_task.delay(instance.id, "movie")
        )
    else: 
        logger.error("erro ao gerar sprites")
        print("mensagem 4")
        return
    
    
@receiver(post_save, sender=Episode)
def episode_post_save(sender, instance, created, **kwargs):
    if not instance.file_episode:
        return logger.error("arquivo não encontrado")


    if created or not instance.duration_all:
        transaction.on_commit(
            lambda: calculate_video_duration.delay(instance.id, "episode")
        )
    else:
        return logger.error("erro na hora da criação")


    if not instance.hls_file:
        transaction.on_commit(
            lambda: process_video_hls_task.delay(instance.id, "episode")
        )
    else: 
        return logger.error("erro ao processar para hls")


    if not instance.sprite_vtt:
        transaction.on_commit(
            lambda: generate_video_sprites_task.delay(instance.id, "episode")
        )
    else: 
        return logger.error("erro ao gerar sprites")
