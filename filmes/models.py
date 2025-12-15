from django.db import models
from slugify import slugify
from cadastro.models import CustomUser
from django.core.validators import MinValueValidator, MaxValueValidator


class Gender(models.Model):
    genders = models.CharField(max_length=50, null=False, blank=False)
    slug = models.CharField(max_length=50, unique=True, null=False, blank=False)

    def __str__(self):
        return self.genders

    def save(self, *args, **kwargs):
        self.slug = slugify(self.genders)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Gender"
        verbose_name_plural = "Genders"


class Movies(models.Model):
    video = models.FileField(upload_to="movies", null=True, blank=True)
    name_movie = models.CharField(max_length=100, blank=False, null=False)
    description = models.CharField(max_length=1000, blank=False, null=False)
    gender = models.ManyToManyField(
        Gender, help_text="para adicionar mais de 1 genero, voce precisa segurar o ctrl"
    )
    poster = models.ImageField(upload_to="posters", blank=False, null=False)
    release_date = models.DateField(blank=True, null=True)
    watch_count = models.PositiveIntegerField(default=0)
    poster_400w = models.CharField(max_length=255, blank=True, null=True) 
    poster_800w = models.CharField(max_length=255, blank=True, null=True)
    poster_1200w = models.CharField(max_length=255, blank=True, null=True)

 

    def get_srcset_urls(self):
        if not self.poster_400w or not self.poster_800w or not self.poster_1200w:
            return ""
            
        return (
            f"{self.poster_400w} 400w,"
            f"{self.poster_800w} 800w,"
            f"{self.poster_1200w} 1200w"
        )
    

    def __str__(self):
        return self.name_movie

    def view_counter(self):
        self.watch_count += 1
        self.save()

    class Meta:
        verbose_name = "Movie"
        verbose_name_plural = "Movies"


class MovieView(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    movie = models.ForeignKey("Movies", on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "movie")


class Avaliacao(models.Model):
    movie_rated = models.ForeignKey(Movies, on_delete=models.CASCADE)
    note = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    data = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Nota {self.note} para {self.movie_rated.name_movie}"


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


class Serie(models.Model):
    name_serie = models.CharField(max_length=100, blank=False, null=False)
    description = models.CharField(max_length=1000, blank=False, null=False)
    gender = models.ManyToManyField(Gender)
    serie_poster = models.ImageField(
        upload_to="series_posters", blank=False, null=False
    )
    poster_400w = models.CharField(max_length=255, blank=True, null=True) 
    poster_800w = models.CharField(max_length=255, blank=True, null=True)
    poster_1200w = models.CharField(max_length=255, blank=True, null=True)

 

    def get_srcset_urls(self):
        if not self.poster_400w or not self.poster_800w or not self.poster_1200w:
            return ""
            
        return (
            f"{self.poster_400w} 400w, "
            f"{self.poster_800w} 800w, "
            f"{self.poster_1200w} 1200w"
        )
    
class Season(models.Model):
    serie = models.ForeignKey(Serie, on_delete=models.CASCADE, related_name="seasons")
    season_number = models.PositiveIntegerField(default=1, unique=True)

    class Meta:
        unique_together = ("serie", "season_number")
        ordering = ["season_number"]

    def __str__(self):
        return f"{self.serie.name_serie} - Temporada {self.season_number}"


class Episode(models.Model):
    season = models.ForeignKey(
        Season, on_delete=models.CASCADE, related_name="episodes"
    )
    episode_number = models.PositiveIntegerField(default=1)
    episode_title = models.CharField(max_length=200)
    episode_video = models.FileField(
        upload_to="series_episodes", null=False, blank=False
    )

    class Meta:
        unique_together = ("season", "episode_number")
        ordering = ["episode_number"]

    def __str__(self):
        return (
            f"S{self.season.season_number}E{self.episode_number}: {self.episode_title}"
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
        return f"{self.user.username} assistiu {self.episode_watched.episode_title}"
