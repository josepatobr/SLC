from django.db import models
from users.models import CustomUser

class Payment(models.Model):
    class Status(models.TextChoices):
        NOTHING = "nothing", ("usuario não fez nenhum pedido")
        PENDING = "pending", ("usuario fez o pedido da compra e esta no aguardo")
        PURCHASED = "purchased", ("compra confirmada e usuario se tornou um vip")
        FAILED = "failed", ("erro na compra, tentaremos novamente e se falhar o dinheiro é devolvido")

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    stripe_checkout_id = models.CharField(max_length=255) 
    status_payment = models.CharField(max_length=20, choices=Status, default='NOTHING') 
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=1.00)
    created_at = models.DateTimeField(auto_now_add=True)