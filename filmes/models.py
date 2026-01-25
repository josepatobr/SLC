from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _
from upload.fields import S3FileField
from users.models import CustomUser
from django.db import models
from slugify import slugify
from uuid import uuid4
import uuid


def get_source_file_path(instance, filename, folder=None):
    video_obj = (
        instance
        if hasattr(instance, "content_object")
        else getattr(instance, "video", None)
    )

    if video_obj and (parent := video_obj.content_object):
        model_name = video_obj.content_type.model.lower()
        path = f"{folder}/{filename}" if folder else filename

        if model_name in ["movies", "serie"]:
            return f"titles/{parent.id}/{path}"

        if model_name == "episode":
            try:
                title_id = parent.season.serie.id
                s_num = parent.season.season_number
                e_num = parent.episode_number
                return f"titles/{title_id}/seasons/{s_num}/{e_num}/{path}"
            except AttributeError:
                pass

    return f"uploads/misc/{uuid4()}/{filename}"


def source_file_path(instance, filename):
    return get_source_file_path(instance, filename)


def hls_playlist_path(instance, filename):
    return get_source_file_path(instance, filename, folder="hls")


def get_sprite_file_path(instance, filename):
    return get_source_file_path(instance, filename, folder="sprites")


def subtitle_file_path(instance, filename):
    lang = slugify(instance.language)
    return get_source_file_path(instance, filename, folder=f"subtitles/{lang}")


class Video(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", ("Pending")
        PROCESSING = "PROCESSING", ("Processing")
        COMPLETED = "COMPLETED", ("Completed")
        FAILED = "FAILED", ("Failed")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=255)
    content_object = GenericForeignKey("content_type", "object_id")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    source_file = S3FileField(upload_to=source_file_path, blank=True, null=True)
    hls_playlist = S3FileField(upload_to=hls_playlist_path, blank=True, null=True)
    processing_error = models.TextField(blank=True)

    def get_sprites(self):
        return self.sprites.all()


class VideoSprite(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name="sprites")
    image = models.ImageField(upload_to=get_sprite_file_path)
    interval = models.PositiveIntegerField(default=10)
    frame_width = models.PositiveIntegerField()
    frame_height = models.PositiveIntegerField()


class VideoTrack(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name="tracks")
    language = models.CharField(max_length=10, default="pt-br")
    label = models.CharField(max_length=50, default="Português")
    subtitle_file = S3FileField(upload_to=subtitle_file_path, blank=True, null=True)


class GenderChoices(models.TextChoices):
        ACAO = 'AC', _('Ação')
        COMEDIA = 'CO', _('Comédia')
        DRAMA = 'DR', _('Drama')
        TERROR = 'TE', _('Terror')
        ROMANCE = 'RO', _('Romance')
        FICCAO = 'FC', _('Ficção Científica')
        DOCUMENTARIO = 'DO', _('Documentário')
        ANIMACAO = 'AN', _('Animação')


class Movies(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name_movie = models.CharField(max_length=100)
    video_record = GenericRelation(Video)
    watch_count = models.PositiveIntegerField(default=0)
    gender = models.CharField(max_length=2, choices=GenderChoices.choices, default=GenderChoices.DRAMA)


class Serie(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name_serie = models.CharField(max_length=100)
    video_record = GenericRelation(Video)
    gender = models.CharField(max_length=2, choices=GenderChoices.choices, default=GenderChoices.DRAMA)


class Season(models.Model):
    serie = models.ForeignKey(Serie, on_delete=models.CASCADE, related_name="seasons")
    season_number = models.PositiveIntegerField(default=1)


class Episode(models.Model):
    season = models.ForeignKey(
        Season, on_delete=models.CASCADE, related_name="episodes"
    )
    episode_number = models.PositiveIntegerField(default=1)
    episode_title = models.CharField(max_length=200)
    video_record = GenericRelation(Video)


class VideoSprite(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid4,
        editable=False,
        help_text=_("Unique identifier for the sprite sheet"),
    )
    video = models.ForeignKey(
        Video,
        on_delete=models.CASCADE,
        related_name="sprites",
        help_text=_("The video this sprite belongs to"),
    )
    image = models.ImageField(
        upload_to=get_sprite_file_path,
        help_text=_("The sprite sheet image file (JPEG)"),
    )
    start_time = models.PositiveIntegerField(
        help_text=_("Time in seconds where this sprite sheet starts (e.g., 0)"),
    )
    end_time = models.PositiveIntegerField(
        help_text=_("Time in seconds where this sprite sheet ends"),
    )
    interval = models.PositiveIntegerField(
        default=10,
        help_text=_("Interval in seconds between each thumbnail"),
    )
    frame_width = models.PositiveIntegerField(
        help_text=_("Width of a single thumbnail in pixels"),
    )
    frame_height = models.PositiveIntegerField(
        help_text=_("Height of a single thumbnail in pixels"),
    )
    columns = models.PositiveIntegerField(
        help_text=_("Number of columns in the sprite sheet grid"),
    )
    rows = models.PositiveIntegerField(
        help_text=_("Number of rows in the sprite sheet grid"),
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Video Sprite")
        verbose_name_plural = _("Video Sprites")
        ordering = ["video", "start_time"]
        constraints = [
            models.UniqueConstraint(
                fields=["video", "start_time"],
                name="unique_sprite_start_time_per_video",
            ),
        ]

    def __str__(self):
        return _("Sprite for %s (%ss - %ss)") % (
            self.video,
            self.start_time,
            self.end_time,
        )


class MoviesWatched(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, verbose_name="Usuário"
    )
    movie_watched = models.ForeignKey(
        Movies, on_delete=models.CASCADE, verbose_name="Filme"
    )
    watched_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Data de Visualização"
    )

    def __str__(self):
        return f"{self.user.username} assistiu {self.movie_watched.name_movie} em {self.watched_at.strftime('%Y-%m-%d')}"


class EpisodeWatched(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, verbose_name="Usuário"
    )
    episode_watched = models.ForeignKey(
        Episode, on_delete=models.CASCADE, verbose_name="Episódio Assistido"
    )
    watched_at = models.DateTimeField(auto_now=True, verbose_name="Última Visualização")

    class Meta:
        unique_together = ("user", "episode_watched")
        ordering = ["-watched_at"]

    def __str__(self):
        return f"{self.user.username} assistiu {self.episode_watched.episode_title}"


