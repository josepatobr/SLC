from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class CadastroSchemas(BaseModel):
    username: str =Field(min_length=3)
    email:EmailStr=Field(min_length=6)
    password:str =Field(min_length=6)
    telefone: Optional[str]

class CadastroOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    access: str
    refresh: str

    class Config:
        orm_mode = True

class LoginEmailSenha(BaseModel):
    email: EmailStr
    password: str

class LoginSMS(BaseModel):
    telefone: str
    codigo: str

class LoginEmailCodigo(BaseModel):
    email: EmailStr
    codigo: str

class LoginOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    access: str
    refresh: str

class CodigoSMSRequest(BaseModel):
    telefone: str

class CodigoEMAILRequest(BaseModel):
    email: EmailStr

class GoogleTokenSchema(BaseModel):
    token: str