from django.core.mail import send_mail
from dotenv import load_dotenv
import os

load_dotenv()


def enviar_email(destinatario, codigo):
    assunto = "Seu código de login"
    mensagem = f"Olá!\n\nSeu código de acesso é: {codigo}\n\nEle expira em 10 minutos."
    remetente = os.getenv("EMAIL_REMETENTE")

    try:
        send_mail(
            subject=assunto,
            message=mensagem,
            from_email=remetente,
            recipient_list=[destinatario],
            fail_silently=False,
        )
        return "Email enviado com sucesso"
    except Exception as e:
        return f"Erro ao enviar email: {str(e)}"
