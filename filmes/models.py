from django.db import models
from slugify import slugify


class Gender(models.Model):
    genders = models.CharField(max_length=50, null=False, blank=False)
    slug = models.CharField(max_length=50, unique=True, null=False, blank=False)

    def _str_(self):
        return self.genders

    def save(self, *args, **kwargs):
        self.slug = slugify(self.genders)
        super().save(*args, **kwargs)


class Movies(models.Model):
    movie = models.FileField(upload_to="movies", null=True, blank=True)
    name_movie = models.CharField(max_length=100, blank=False, null=False)
    description = models.CharField(max_length=1000, blank=False, null=False)
    gender = models.ManyToManyField(Gender)
    poster = models.ImageField(upload_to="posters", blank=False, null=False)
    release_date = models.DateField(blank=True, null=True)
    watch_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name_movie

    def view_counter(self):
        self.watch_count += 1
        self.save()
