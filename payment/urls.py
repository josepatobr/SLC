from django.urls import path
from . import views

urlpatterns = [
    path("success/", views.payment_success, name="success"),
    path("cancel/", views.payment_cancel, name="cancel"),
    path("checkout/", views.checkout, name="checkout"),
]
