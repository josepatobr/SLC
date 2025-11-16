from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class CadastroSchemas(BaseModel):
    full_name: str = Field(max_length=200)
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    cpf: str = Field(min_length=11, max_length=11)
    password: str = Field(min_length=6)
    telefone: Optional[str] = Field(None, max_length=15)


class LoginEmailSenha(BaseModel):
    email: EmailStr
    password: str


class CodigoBase(BaseModel):
    codigo: str = Field(min_length=6, max_length=6)


class LoginSMS(CodigoBase):
    telefone: str


class LoginEmailCodigo(CodigoBase):
    email: EmailStr


class CodigoRequest(BaseModel):
    telefone: Optional[str] = Field(default=None)
    email: Optional[EmailStr] = Field(default=None)


class GoogleTokenSchema(BaseModel):
    token: str


class AuthOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    access: str
    refresh: str

    class Config:
        orm_mode = True
