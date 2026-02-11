from .tasks import (
    calculate_video_duration,
    generate_video_sprites_task,
    process_video_hls_task,
)
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from .models import Movies, Episode


@receiver(post_save, sender=Movies)
def movie_post_save(sender, instance, created, **kwargs):
    if instance.file_movie:
        if created or not instance.duration_all:
            transaction.on_commit(
                lambda: calculate_video_duration.delay(instance.id, "movie")
            )

        if not instance.hls_file:
            transaction.on_commit(
                lambda: process_video_hls_task.delay(instance.id, "movie")
            )

        if not instance.sprite_vtt:
            transaction.on_commit(
                lambda: generate_video_sprites_task.delay(instance.id, "movie")
            )


@receiver(post_save, sender=Episode)
def episode_post_save(sender, instance, created, **kwargs):
    if instance.file_episode:
        if created or not instance.duration_all:
            transaction.on_commit(
                lambda: calculate_video_duration.delay(instance.id, "episode")
            )

        if not instance.hls_file:
            transaction.on_commit(
                lambda: process_video_hls_task.delay(instance.id, "episode")
            )

        if not instance.sprite_vtt:
            transaction.on_commit(
                lambda: generate_video_sprites_task.delay(instance.id, "episode")
            )
