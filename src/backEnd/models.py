from pydantic import BaseModel, Field
from typing import Optional

class PropertyCreate (BaseModel):
    address: str = Field(..., min_length=10, max_length=255, description="Endereço da propriedade")
    contact: str = Field(..., max_length=20, description="Contato da imobiliaria")
    property_name: Optional[str] = Field(None, max_length=255, description="Nome da propriedade")
    value_per_day: int = Field(..., gt=0, description="Valor de alguel diário da propriedade")

class PropertyUpdate (BaseModel):
    address: Optional[str] = Field(None, min_length=10, max_length=255, description="Endereço da propriedade")
    contact: Optional[str] = Field(None, max_length=20, description="Contato da imobiliaria")
    property_name: Optional[str] = Field(None, max_length=255, description="Nome da propriedade")
    value_per_day: Optional[int] = Field(None, gt=0, description="Valor de alguel diário da propriedade")
