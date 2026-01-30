from django.contrib.auth.models import AbstractUser
from .managers import UserManager
from django.db import models
from typing import ClassVar
from django import forms


class CustomUser(AbstractUser):
    class UserStatus(models.TextChoices):
        USER_COMUM = "user_comum", ("usuario comum, ainda sem pagar")
        BETA_TEST = "beta_test", ("usuario de testes")
        USER_VIP = "user_vip", ("usuario vip")

    username = None
    full_name = models.CharField(max_length=200, unique=False, null=True, blank=True)
    email = models.EmailField(("email address"), unique=True)
    profile_picture = models.ImageField(
        upload_to="profile_picture", blank=True, null=True
    )
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    stripe_customer_id = models.CharField(
        max_length=100, blank=True, null=True, unique=True
    )
    user_status = models.CharField(
        max_length=20, choices=UserStatus, default=UserStatus.USER_COMUM
    )
    objects: ClassVar[UserManager] = UserManager()

    def __str__(self):
        return str(self.username)

    @property
    def is_vip(self):
        return self.user_status == self.UserStatus.USER_VIP

    @property
    def not_vip(self):
        return self.user_status == self.UserStatus.USER_COMUM

    @property
    def is_beta(self):
        return self.user_status == self.UserStatus.BETA_TEST


class CustomUserChangeForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ["full_name", "email", "profile_picture"]
