from django.urls import path
from . import views

urlpatterns = [
    path('success.html', views.payment_success),
    path('cancel.html', views.payment_cancel),
    path('checkout.html', views.checkout),
]
