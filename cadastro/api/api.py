from cadastro.api.schemas import CadastroOut, CadastroSchemas, LoginEmailSenha, LoginSMS, CodigoSMSRequest, CodigoEMAILRequest, GoogleTokenSchema, LoginEmailCodigo
from rest_framework_simplejwt.tokens import RefreshToken
from ninja import Router
import random
from cadastro.models import CodigoSMS, CustomUser, CodigoEmail
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from cadastro.tasks import enviar_sms_async, enviar_email_async
from dotenv import load_dotenv
import os
from django.shortcuts import redirect

load_dotenv()
router = Router()

@router.post("cadastro/", response=CadastroOut)
def cadastro(request, payload:CadastroSchemas):
    if request.user and request.user.is_authenticated:
        return redirect("home/")

    if CustomUser.objects.filter(telefone=payload.telefone).exists():
        return {"erro": "Telefone já cadastrado"}

    if CustomUser.objects.filter(email=payload.email).exists():
        return {"erro": "email ja cadastrado"}

    else:
        user = CustomUser.objects.create_user(
            username=payload.username, email=payload.email, password=payload.password
        )
        user.telefone = payload.telefone
        user.save()
        refresh = RefreshToken.for_user(user)
        return CadastroOut(
            id=user.id,
            username=user.username,
            email=user.email,
            access=str(refresh.access_token),
            refresh=str(refresh),
        )

@router.post("login-email/")
def login_email(request, payload:LoginEmailSenha):
    if request.user and request.user.is_authenticated:
        return redirect("home/")

    try:
        user = CustomUser.objects.get(email=payload.email)
    except CustomUser.DoesNotExist:
        return {"erro": "Email não encontrado"}

    if not user.check_password(payload.password):
        return {"erro": "Senha incorreta"}

    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "usuario": user.username,
    }

@router.post("login-sms/")
def login_sms(request, payload:LoginSMS):
    if request.user and request.user.is_authenticated:
        return redirect("home/")

    try:
        codigo_obj = CodigoSMS.objects.filter(
            telefone=payload.telefone, codigo=payload.codigo
        ).latest("criado_em")
    except CodigoSMS.DoesNotExist:
        return {"erro": "Código inválido ou não encontrado"}

    if not codigo_obj.esta_valido():
        return {"erro": "Código expirado"}

    try:
        user = CustomUser.objects.get(telefone=payload.telefone)
    except CustomUser.DoesNotExist:
        return {"erro": "Usuário não encontrado"}

    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "usuario": user.email,
    }

@router.post("enviar-codigo-sms/")
def enviar_codigo(request, payload:CodigoSMSRequest):
    numero = payload.telefone
    codigo = str(random.randint(100000, 999999))

    enviar_sms_async.delay(numero, codigo)

    codigo_obj = CodigoSMS.objects.create(telefone=numero, codigo=codigo, expires_at=5)
    codigo_obj = CodigoSMS(telefone=numero, codigo=codigo)
    codigo_obj.salvar_codigo()
    return {"status": "Código enviado"}

@router.post("enviar-codigo-email/")
def enviar_codigo_email(request, payload:CodigoEMAILRequest):
    email = payload.email
    codigo = str(random.randint(100000, 999999))

    enviar_email_async.delay(email, codigo)
    codigo_obj = CodigoEmail.objects.create(email=email, codigo=codigo)
    codigo_obj.salvar_codigo_email()

    return {"status": "Código enviado"}

@router.post("login-google/")
def login_google(request, payload:GoogleTokenSchema):
    token = payload.token

    if request.user and request.user.is_authenticated:
        return redirect("home/")

    if not token:
        return {"error": "Token não fornecido"}

    try:
        idinfo = id_token.verify_oauth2_token(
            payload.token, google_requests.Request(), os.getenv("GOOGLE_CLIENT_ID")
        )

        username = idinfo.get("name", "")
        email = idinfo.get("email")
        telefone = ""

        user, created = CustomUser.objects.get_or_create(email=email)

        if created:
            user.username = username
            user.email = email
            user.telefone = telefone
            user.save()
            return redirect("home/")

        if idinfo["aud"] != os.getenv("GOOGLE_CLIENT_ID"):
            return {"error": "Token com audience inválido"}

        refresh = RefreshToken.for_user(user)
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "usuario": email,
        }

    except Exception as e:
        return {"error": str(e)}


@router.post("login-email-codigo/")
def login_email_codigo(request, payload:LoginEmailCodigo):
    if request.user and request.user.is_authenticated:
        return redirect("home/")

    try:
        codigo_obj = CodigoEmail.objects.filter(
            email=payload.email, codigo=payload.codigo
        ).latest("criado_em")
    except CodigoEmail.DoesNotExist:
        return {"erro": "Código inválido ou não encontrado"}

    if not codigo_obj.esta_valido():
        return {"erro": "Código expirado"}

    try:
        user = CustomUser.objects.get(email=payload.email)
    except CustomUser.DoesNotExist:
        return {"error": "Usuário não encontrado"}

    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "usuario": user.username,
    }
