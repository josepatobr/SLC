from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpRequest
from django.contrib.auth.decorators import login_required
from .models import CustomUser
from .models import Payment
from django.conf import settings
import stripe

stripe.api_key = settings.KEY_SECRET_STRIPE


@login_required
def checkout(request: HttpRequest):
    user: CustomUser = request.user
    display_name = user.full_name or user.email

    try:
        if not user.stripe_customer_id:
            customer = stripe.Customer.create(
                email=user.email,
                name=display_name,
            )
            user.stripe_customer_id = customer.id
            user.save(update_fields=["stripe_customer_id"])

        checkout_session = stripe.checkout.Session.create(
            customer=user.stripe_customer_id,
            currency="BRL",
            payment_method_types=["card"],
            ui_mode="hosted",
            mode="payment",
            line_items=[
                {
                    "price_data": {
                        "currency": "BRL",
                        "unit_amount": 100,
                        "product_data": {
                            "name": "SLC VIP",
                            "description": "Acesso ilimitado por 1 mês",
                        },
                    },
                    "quantity": 1,
                }
            ],
            success_url=reverse("success"),
            cancel_url=reverse("cancel"),
        )

        Payment.objects.create(
            user=user,
            stripe_checkout_id=checkout_session.id,
            status_payment=Payment.Status.PENDING,
            amount=1.00,
        )
        return render(request, "checkout.html", {"checkout_url": checkout_session.url})
    except Exception as e:
        print(e)
        return redirect("cancel")


def payment_success(request):
    return render(request, "success.html")


def payment_cancel(request):
    return render(request, "cancel.html")
