from django.contrib.auth.models import AbstractUser
from django.db import models



class CustomUser(AbstractUser):
    full_name = models.CharField(max_length=200, unique=False, null=True, blank=True)
    profile_picture = models.ImageField(
        upload_to="profile_picture", blank=True, null=True
    )