import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def enviar_sms(numero, codigo):
    URL = "https://api.smsdev.com.br/v1/send"
    EXPIRATION_MINUTES = 5

    mensagem = f"Seu código de login é: {codigo}. Válido por {EXPIRATION_MINUTES} min. Nao compartilhe."

    params = {
        "key": settings.SMS_KEY,
        "type": "text",
        "number": numero,
        "msg": mensagem,
    }

    try:
        response = requests.get(URL, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()

        if data.get("status") == "200" or data.get("retorno") == "OK":
            logger.info(f"SMS enviado com sucesso para {numero}. Resposta: {data}")
            return True
        else:
            logger.error(f"Falha na API SMSDev para {numero}. Resposta: {data}")
            raise Exception(
                f"SMSDev falhou: {data.get('retorno', 'Erro desconhecido')}"
            )

    except requests.exceptions.RequestException as e:
        logger.error(f"Erro de conexão/HTTP ao enviar SMS para {numero}: {e}")
        raise Exception(f"Falha de rede/HTTP ao enviar SMS: {e}")
    except Exception as e:
        logger.error(f"Erro interno ao processar envio de SMS para {numero}: {e}")
        raise
