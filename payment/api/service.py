from django.shortcuts import redirect
from django.http import HttpResponse
from users.models import CustomUser
from django.conf import settings
from ninja import NinjaAPI
import stripe


stripe.api_key = getattr(settings, "KEY_SECRET_STRIPE")
stripe_api = NinjaAPI()


YOUR_DOMAIN = "http://localhost:8000"


@stripe_api.post("/create-checkout-session")
def create_checkout_session(request):
    user = request.user
    display_name = user.full_name if user.full_name else user.username

    try:
        customer = stripe.Customer.create(
            email=user.email,
            name=display_name,
        )

        user.stripe_customer_id = customer.id
        user.save()

        checkout_session = stripe.checkout.Session.create(
            customer=customer.id,
            line_items=[
                {
                    "price_data": {
                        "currency": "brl",
                        "unit_amount": 50,
                        "product_data": {
                            "name": "SLC VIP",
                            "description": "Acesso ilimitado por 1 mês",
                        },
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            payment_intent_data={
                "setup_future_usage": "off_session",
            },
            success_url=YOUR_DOMAIN + "/success.html",
            cancel_url=YOUR_DOMAIN + "/cancel.html",
        )
        return redirect(checkout_session.url)
    except Exception as e:
        return {"error": str(e)}


@stripe_api.post("/stripe-webhook", csrf_exempt=True)
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
    endpoint_secret = getattr(settings, "ENDPOINT_SECRET")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except Exception as e:
        return HttpResponse(status=400)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        customer_id = session.get("customer")
        try:
            user = CustomUser.objects.get(stripe_customer_id=customer_id)

            user.user_status = "USER_VIP"
            user.save()

            print(f"Pagamento confirmado! Usuário {user.username} agora é VIP.")
        except CustomUser.DoesNotExist:
            print("Erro: Cliente Stripe não encontrado no nosso banco de dados.")

    return HttpResponse(status=200)


@stripe_api.post("/charge-saved-card/{customer_id}")
def charge_saved_card(request, customer_id: str, payment_method_id: str):
    try:
        payment_intent = stripe.PaymentIntent.create(
            amount="1099",
            currency="brl",
            customer=customer_id,
            payment_method=payment_method_id,
            off_session=True,
            confirm=True,
        )
        return {"status": "success", "id": payment_intent.id}
    except stripe.error.CardError as e:
        return {"error": "Cartão recusado ou requer autenticação 3DS"}
