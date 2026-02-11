from django.utils.translation import gettext_lazy as _
from django.db import models
from uuid import uuid4
from datetime import timedelta
from django.db import transaction
from .tasks import process_video_hls_task, calculate_video_duration
from users.models import CustomUser


def get_source_file_path(instance, filename, folder=None):
    model_name = instance._meta.model_name
    path = f"{folder}/{filename}" if folder else filename

    if model_name == "movies":
        return f"titles_{instance.id}/{path}"

    if model_name == "episode":
        try:
            title_id = instance.series.id
            s_num = instance.season_number
            e_num = instance.episode_number
            return f"titles_{title_id}/season_{s_num}/ep_{e_num}/{path}"
        except AttributeError:
            pass

    return f"uploads/misc/{uuid4()}/{filename}"


class Status(models.TextChoices):
    TERMINADO = "terminado", "Terminado"
    AINDA_LANCANDO = "ainda_lancando", "ainda lançando"
    EM_BREVE = "em_breve", "Em breve"
    DISPONIVEL = "disponivel", "disponivel"


class Genero(models.TextChoices):
    SEM_GENERO = "sem_genero", "sem genero"
    ROMANCE = "romance", "romance"


class Movies(models.Model):
    title = models.CharField(max_length=200, blank=False, null=False)
    description = models.TextField(blank=False, null=False)

    status_movie = models.CharField(choices=Status, blank=False, null=False)
    gener_movie = models.CharField(choices=Genero, blank=True, null=True)

    file_movie = models.FileField(upload_to=get_source_file_path)
    hls_file = models.CharField(max_length=500, blank=True, null=True)
    sprite_vtt = models.CharField(max_length=500, null=True, blank=True)

    duration_all = models.DurationField(null=True, blank=True)
    current_time = models.DurationField(default=timedelta(seconds=0))

    @property
    def duration_in_minutes(self):
        if self.duration_all:
            return int(self.duration_all.total_seconds() // 60)
        return 0

    def save(self, *args, **kwargs):
        is_new_video = False
        if not self.pk:
            is_new_video = True
        else:
            old_instance = Movies.objects.get(pk=self.pk)
            if old_instance.file_movie != self.file_movie:
                is_new_video = True

        super().save(*args, **kwargs)

        if is_new_video and self.file_movie:
            transaction.on_commit(
                lambda: calculate_video_duration.delay(self.id, "movie")
            )
            transaction.on_commit(
                lambda: process_video_hls_task.delay(self.id, "movie")
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
        return f"{self.user.username} assistiu {self.movie_watched.title} em {self.watched_at.strftime('%Y-%m-%d')}"


class Series(models.Model):
    title_serie = models.CharField(max_length=200)
    description = models.TextField()

    status_series = models.CharField(max_length=20, choices=Status.choices)
    gener_serie = models.CharField(choices=Genero, blank=True, null=True)


class Episode(models.Model):
    series = models.ForeignKey(
        Series, on_delete=models.CASCADE, related_name="episodes"
    )
    title_episode = models.CharField(max_length=200)

    season_number = models.PositiveIntegerField(default=1)
    episode_number = models.PositiveIntegerField()

    hls_file = models.CharField(max_length=500, blank=True, null=True)
    file_episode = models.FileField(upload_to=get_source_file_path)
    sprite_vtt = models.CharField(max_length=500, null=True, blank=True)

    duration_all = models.DurationField(null=True, blank=True)
    current_time = models.DurationField(default=timedelta(seconds=0))

    @property
    def duration_in_minutes(self):
        if self.duration_all:
            return int(self.duration_all.total_seconds() // 60)
        return 0

    def save(self, *args, **kwargs):
        is_new_video = False
        if not self.pk:
            is_new_video = True
        else:
            old_instance = Episode.objects.get(pk=self.pk)
            if old_instance.file_episode != self.file_episode:
                is_new_video = True

        super().save(*args, **kwargs)

        if is_new_video and self.file_episode:
            transaction.on_commit(
                lambda: calculate_video_duration.delay(self.id, "episode")
            )
            transaction.on_commit(
                lambda: process_video_hls_task.delay(self.id, "episode")
            )


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
        return f"{self.user.username} assistiu {self.episode_watched.title_episode}"


class VideoSprite(models.Model):
    movie = models.ForeignKey(
        "Movies",
        on_delete=models.CASCADE,
        related_name="sprites",
        null=True,
        blank=True,
    )
    episode = models.ForeignKey(
        "Episode",
        on_delete=models.CASCADE,
        related_name="sprites",
        null=True,
        blank=True,
    )

    start_time = models.FloatField(_("Início (s)"))
    end_time = models.FloatField(_("Fim (s)"))
    interval = models.PositiveIntegerField(_("Intervalo"), default=10)

    columns = models.PositiveIntegerField(_("Colunas"), default=5)
    rows = models.PositiveIntegerField(_("Linhas"), default=1)
    frame_width = models.PositiveIntegerField(_("Largura do Frame"), default=160)

    image = models.ImageField(_("Imagem"), upload_to="sprites/%Y/%m/%d/")

    class Meta:
        verbose_name = _("Sprite Sheet")
        verbose_name_plural = _("Sprite Sheets")
        ordering = ["start_time"]

    def __str__(self):
        return f"Sprite {self.start_time}s - {self.end_time}s"



