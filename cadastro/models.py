from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta


class CustomUser(AbstractUser):
    telefone = models.CharField(max_length=20)


class Codigo_Selecionado(models.Model):
    telefone = models.CharField(max_length=11)
    email = models.EmailField(max_length=200)

    def __str__(self):
        return self.email


class Codigo(models.Model):
    resultado = models.ForeignKey(Codigo_Selecionado, on_delete=models.CASCADE)
    codigo = models.CharField(max_length=6)
    criado_em = models.DateTimeField(auto_now_add=True)
    expira_em = models.DateTimeField()

    def salvar_codigo(self):
        self.expira_em = timezone.now() + timedelta(minutes=5)
        self.save()

    def esta_valido(self):
        return timezone.now() <= self.expira_em

    def __str__(self):
        return f"{self.resultado} - {self.codigo}"
