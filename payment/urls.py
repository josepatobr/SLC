from django.urls import path
from . import views

urlpatterns = [
    path('success/', views.payment_success),
    path('cancel/', views.payment_cancel),
    path('checkout/', views.checkout, name="checkout"),
]
