from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django import forms


class CustomUser(AbstractUser):
    full_name = models.CharField(max_length=200, unique=False, null=True, blank=True)
    telefone = models.CharField(max_length=15, null=True, blank=True)
    profile_picture = models.ImageField(
        upload_to="profile_picture", blank=True, null=True
    )

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"


class CustomUserChangeForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ("full_name", "username", "email", "telefone", "profile_picture")


class Codigo(models.Model):
    email = models.EmailField(max_length=200, null=True, blank=True)
    telefone = models.CharField(max_length=15, null=True, blank=True)

    codigo = models.CharField(max_length=6)
    criado_em = models.DateTimeField(auto_now_add=True)
    expira_em = models.DateTimeField()

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(email__isnull=False) | models.Q(telefone__isnull=False),
                name="email_ou_telefone_requerido",
            )
        ]

    def esta_valido(self):
        return timezone.now() <= self.expira_em

    def __str__(self):
        contato = self.email if self.email else self.telefone
        return f"Código {self.codigo} para {contato}"
