from dotenv import load_dotenv
from django.template.loader import render_to_string

load_dotenv()


def enviar_email(destinatario, codigo):
    EXPIRATION_MINUTES = 5

    context = {
        "codigo": codigo,
        "expiracao_minutos": EXPIRATION_MINUTES,
        "username": destinatario.split("@")[0],
    }

    html_content = render_to_string("email/codigo_login.html", context)
