from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class CustomUser(AbstractUser):
    telefone = models.CharField(max_length=15, unique=True, null=True, blank=True)


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
