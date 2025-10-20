from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta


class CustomUser(AbstractUser):
    telefone = models.CharField(max_length=20)


class CodigoSMS(models.Model):
    telefone = models.CharField(max_length=20)
    codigo = models.CharField(max_length=6)
    criado_em = models.DateTimeField(auto_now_add=True)
    expira_em = models.DateTimeField()

    def salvar_codigo(self):
        self.expira_em = timezone.now() + timedelta(minutes=5)
        self.save()

    def esta_valido(self):
        return timezone.now() <= self.expira_em

    def __str__(self):
        return f"{self.telefone} - {self.codigo}"
    

class CodigoEmail(models.Model):
    email = models.EmailField()
    codigo = models.CharField(max_length=6)
    criado_em = models.DateTimeField(auto_now_add=True)

    def esta_valido(self):
        return timezone.now() - self.criado_em < timedelta(minutes=10)
    
    def salvar_codigo_email(self):
        self.save()