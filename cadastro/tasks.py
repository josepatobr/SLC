from celery import shared_task
from cadastro.envios.sms_service import enviar_sms
from cadastro.envios.email_service import enviar_email


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def enviar_sms_async(self, numero, codigo):
    try:
        return enviar_sms(numero, codigo)
    except Exception as exc:
        raise self.retry(exc=exc)


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def enviar_email_async(self, email, codigo):
    try:
        return enviar_email(email, codigo)
    except Exception as exc:
        raise self.retry(exc=exc)
