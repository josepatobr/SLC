import requests
from dotenv import load_dotenv
import os

load_dotenv()
def enviar_sms(numero, codigo):
    url = "https://api.smsdev.com.br/v1/send"
    params = {
        "key": os.getenv("SMS_KEY"),
        "type": "text",
        "number": numero,
        "msg": f"Seu código de login é: {codigo}"
    }
    response = requests.get(url, params=params)
    return response.json()