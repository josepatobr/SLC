from celery import shared_task
from cadastro.envios.email_service import enviar_email
from cadastro.envios.sms_service import enviar_sms


@shared_task
def enviar_sms_async(numero, codigo):
    return enviar_sms(numero, codigo)


@shared_task
def enviar_email_async(email, codigo):
    return enviar_email(email, codigo)
