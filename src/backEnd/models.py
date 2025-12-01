from pydantic import BaseModel, Field
from typing import Optional

class PropertyCreate (BaseModel):
    address: str = Field(..., min_length=1, max_length=255, description="Endereço da propriedade")
    contact: str = Field(..., max_length=20, description="Contato da imobiliaria")
    property_name: Optional[str] = Field(None, max_length=255, description="Nome da propriedade")
    value_per_day: int = Field(..., gt=0, description="Valor de alguel diário da propriedade")
    capacity: int = Field(..., gt=0, description="Capacidade do imovel")

class PropertyUpdate (BaseModel):
    contact: Optional[str] = Field(None, max_length=20, description="Contato da imobiliaria")
    property_name: Optional[str] = Field(None, max_length=255, description="Nome da propriedade")
    value_per_day: Optional[int] = Field(None, gt=0, description="Valor de alguel diário da propriedade")
    capacity: Optional[int] = Field(None, gt=0, description="Capacidade do imovel")

class ClientCreate (BaseModel):
    email: str = Field(..., max_length=255, description="E-mail do cliente")
    password: str = Field(..., min_length=5, max_length=255, description="Senha do cliente")
    CPF: str = Field(..., max_length=11, description="CPF do cliente")
    numeroTel: str = Field(..., max_length=20, description="Contato do cliente")
    nome: str = Field(..., max_length=255, description="Nome do cliente")
    isAdmin: Optional[bool] = Field(None, description="Cliente é admin")
    filial: str = Field(..., max_length=5, description="Filial do cliente")
    wallet: Optional[int] = Field(None, description="Saldo do cliente")

class ClientUpdate (BaseModel):
    email: Optional[str] = Field(None, max_length=255, description="E-mail do cliente")
    password: Optional[str] = Field(None, min_length=4, max_length=255, description="Senha do cliente")
    numeroTel: Optional[str] = Field(None, max_length=20, description="Contato do cliente")
    nome: Optional[str] = Field(None, max_length=255, description="Nome do cliente")
    isAdmin: Optional[bool] = Field(None, description="Cliente é admin")
    filial: Optional[str] = Field(None, max_length=5, description="Filial do cliente")
    wallet: Optional[int] = Field(None, description="Saldo do cliente")

class PropertyReserveCreate (BaseModel):
    renter_id: int = Field(..., description="Id do titular da reserva")
    property_id: int = Field(..., description="Id da propriedade")
    initTime: str = Field(..., description="Início da reserva")
    endTime: str = Field(..., description="Fim da reserva")

class PaymentCreate (BaseModel):
    value: int = Field(..., description="Valor da reserva")
    renter_id: int = Field(..., description="Id do titular da reserva")
    reserve_id: int = Field(..., description="Id da reserva")

class Login(BaseModel):
        email: str
        password: str
