import requests
from dotenv import load_dotenv
from django.conf import settings


load_dotenv()


def enviar_sms(numero, codigo):
    url = "https://api.smsdev.com.br/v1/send"
    params = {
        "key": settings("SMS_KEY"),
        "type": "text",
        "number": numero,
        "msg": f"Seu código de login é: {codigo}",
    }
    response = requests.get(url, params=params)
    return response.json()
