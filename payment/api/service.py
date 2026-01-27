from django.http import HttpResponse, JsonResponse
from ninja.security import django_auth
from users.models import CustomUser
from payment.models import Payment
from django.conf import settings
from ninja import Router
import stripe


stripe.api_key = getattr(settings, "KEY_SECRET_STRIPE")
stripe_api = Router(auth=django_auth)


YOUR_DOMAIN = getattr(settings, "YOUR_DOMAIN")


@stripe_api.post("create-checkout-session/")
def create_checkout_session(request):
    user = request.user
    display_name = user.full_name if user.full_name else user.email
    
    try:
        if not user.stripe_customer_id:
            customer = stripe.Customer.create(
                email=user.email,
                name=display_name,
            )
            user.stripe_customer_id = customer.id
            user.save()

        checkout_session = stripe.checkout.Session.create(
            customer=user.stripe_customer_id,
            line_items=[
                {
                    "price_data": {
                        "currency": "brl",
                        "unit_amount": 100,
                        "product_data": {
                            "name": "SLC VIP",
                            "description": "Acesso ilimitado por 1 mês",
                        },
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url=YOUR_DOMAIN + "/payment/success/",
            cancel_url=YOUR_DOMAIN + "/payment/cancel/",
        )

        Payment.objects.create(
            user=user,
            stripe_checkout_id=checkout_session.id,
            status_payment=Payment.Status.PENDING,
            amount=1.00
        )

        return JsonResponse({'url': checkout_session.url})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@stripe_api.post("stripe-webhook/")
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
        checkout_id = session.get("id") 

        try:
            pagamento = Payment.objects.get(stripe_checkout_id=checkout_id)
                        
            pagamento.status = Payment.Status.PURCHASED
            pagamento.save()

            user = pagamento.user
            user.user_status = CustomUser.UserStatus.USER_VIP
            user.save()

            return {"message": f"Pagamento {checkout_id} confirmado! {user.email} agora é VIP."}
        except CustomUser.DoesNotExist:
            return("Erro: Cliente Stripe não encontrado no nosso banco de dados.")
        except Payment.DoesNotExist:
            return(f"ERRO CRÍTICO: Pagamento {checkout_id} confirmado no Stripe, mas não existe no banco!")

    elif event["type"] in ["checkout.session.async_payment_failed", "payment_intent.payment_failed"]:
            session = event["data"]["object"]
            checkout_id = session.get("id") or session.get("metadata", {}).get("checkout_id")
                
            pagamento = Payment.objects.filter(stripe_checkout_id=checkout_id).first()
            if pagamento:
                pagamento.status = Payment.Status.FAILED
                pagamento.save()


@stripe_api.post("charge-saved-card/{customer_id}")
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
