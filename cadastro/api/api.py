from cadastro.api.schemas import (
    AuthOut,
    CadastroSchemas,
    LoginEmailSenha,
    LoginSMS,
    CodigoRequest,
    GoogleTokenSchema,
    LoginEmailCodigo,
)
from rest_framework_simplejwt.tokens import RefreshToken
from ninja import Router
import random
from cadastro.models import CustomUser, Codigo
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from cadastro.tasks import enviar_sms_async, enviar_email_async
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from ninja.errors import HttpError
from django.shortcuts import redirect, resolve_url

router = Router()
COOLDOWN_MINUTES = 1


@router.post("cadastro/", response=AuthOut)
def cadastro(request, payload: CadastroSchemas):
    if request.user and request.user.is_authenticated:
        return redirect(resolve_url("home"))
    if CustomUser.objects.filter(telefone=payload.telefone).exists():
        raise HttpError(400, "Telefone já cadastrado")

    if CustomUser.objects.filter(email=payload.email).exists():
        raise HttpError(400, "Email já cadastrado")

    user = CustomUser.objects.create_user(
        username=payload.username,
        email=payload.email,
        password=payload.password,
        telefone=payload.telefone,
    )
    user.save()

    refresh = RefreshToken.for_user(user)

    return AuthOut(
        id=user.id,
        username=user.username,
        email=user.email,
        access=str(refresh.access_token),
        refresh=str(refresh),
    )


@router.post("login-email/")
def login_email(request, payload: LoginEmailSenha):
    if request.user and request.user.is_authenticated:
        return redirect(resolve_url("home"))

    try:
        user = CustomUser.objects.get(email=payload.email)
    except CustomUser.DoesNotExist:
        raise HttpError(401, "Credenciais inválidas")

    if not user.check_password(payload.password):
        raise HttpError(401, "Credenciais inválidas")

    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "usuario": user.username,
    }


@router.post("login-sms/")
def login_sms(request, payload: LoginSMS):
    if request.user and request.user.is_authenticated:
        return redirect(resolve_url("home"))

    GENERIC_ERROR = "Credenciais inválidas ou código expirado."

    try:
        codigo_obj = Codigo.objects.filter(
            telefone=payload.telefone, codigo=payload.codigo
        ).latest("criado_em")
    except Codigo.DoesNotExist:
        raise HttpError(401, GENERIC_ERROR)

    if not codigo_obj.esta_valido():
        raise HttpError(401, GENERIC_ERROR)

    try:
        user = CustomUser.objects.get(telefone=payload.telefone)
    except CustomUser.DoesNotExist:
        raise HttpError(401, GENERIC_ERROR)

    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "usuario": user.email,
    }


@router.post("enviar-codigo/")
def enviar_codigo(request, payload: CodigoRequest):
    if not payload.email and not payload.telefone:
        raise HttpError(400, "Nenhum email ou telefone foi fornecido.")

    contato_valor = payload.email if payload.email else payload.telefone
    contato_campo = "email" if payload.email else "telefone"

    try:
        Codigo.objects.filter(**{contato_campo: contato_valor}).latest("criado_em")
    except Codigo.DoesNotExist:
        pass
    else:
        latest_codigo = Codigo.objects.filter(**{contato_campo: contato_valor}).latest(
            "criado_em"
        )

        if latest_codigo.criado_em > timezone.now() - timedelta(
            minutes=COOLDOWN_MINUTES
        ):
            raise HttpError(
                429,
                f"Aguarde {COOLDOWN_MINUTES} minuto(s) antes de solicitar um novo código.",
            )

    codigo = str(random.randint(100000, 999999))
    expiracao = timezone.now() + timedelta(minutes=5)

    codigo_kwargs = {
        contato_campo: contato_valor,
        "codigo": codigo,
        "expira_em": expiracao,
    }

    Codigo.objects.create(**codigo_kwargs)

    if payload.email:
        enviar_email_async.delay(contato_valor, codigo)
    elif payload.telefone:
        enviar_sms_async.delay(contato_valor, codigo)

    return {"status": "Código enviado com sucesso"}


@router.post("login-google/")
def login_google(request, payload: GoogleTokenSchema):
    if request.user and request.user.is_authenticated:
        return redirect(resolve_url("home"))

    token = payload.token

    if not token:
        raise HttpError(400, "Token não fornecido")

    try:
        idinfo = id_token.verify_oauth2_token(
            token, google_requests.Request(), settings("GOOGLE_CLIENT_ID")
        )

        if idinfo["aud"] != settings("GOOGLE_CLIENT_ID"):
            raise HttpError(401, "Token de Google inválido (Audience mismatch)")

        username = idinfo.get("name", "")
        email = idinfo.get("email")
        telefone = idinfo.get("phone", "")

        user, created = CustomUser.objects.get_or_create(
            email=email,
            defaults={
                "username": username,
                "telefone": telefone,
            },
        )

        if created:
            pass
        refresh = RefreshToken.for_user(user)

        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "usuario": user.email,
        }

    except HttpError:
        raise
    except Exception:
        raise HttpError(401, "Falha na validação do token Google")


@router.post("login-email-codigo/")
def login_email_codigo(request, payload: LoginEmailCodigo):
    if request.user and request.user.is_authenticated:
        return redirect(resolve_url("home"))

    GENERIC_ERROR = "Credenciais inválidas ou código expirado."

    try:
        codigo_obj = Codigo.objects.filter(
            email=payload.email, codigo=payload.codigo
        ).latest("criado_em")
    except Codigo.DoesNotExist:
        raise HttpError(401, GENERIC_ERROR)

    if not codigo_obj.esta_valido():
        raise HttpError(401, GENERIC_ERROR)

    try:
        user = CustomUser.objects.get(email=payload.email)
    except CustomUser.DoesNotExist:
        raise HttpError(401, GENERIC_ERROR)

    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "usuario": user.username,
    }
