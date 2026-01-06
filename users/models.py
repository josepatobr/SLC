from django.contrib.auth.models import AbstractUser
from django.db import models
from .managers import UserManager
from typing import ClassVar

class CustomUser(AbstractUser):
    username = None
    full_name = models.CharField(max_length=200, unique=False, null=True, blank=True)
    email = models.EmailField(("email address"), unique=True)
    profile_picture = models.ImageField(
        upload_to="profile_picture", blank=True, null=True
    )
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects: ClassVar[UserManager] = UserManager()

    def __str__(self):
        return str(self.username) if self.username else str(self.email)
    
