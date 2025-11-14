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



class Avaliação(models.Model):
    movie_rated = models.ForeignKey(Movies, on_delete=models.CASCADE)
    note = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)]) 
    data = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Nota {self.note} para {self.movie_rated.name_movie}"