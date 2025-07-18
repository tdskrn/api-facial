# Modelo de dados para funcionário
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Employee(BaseModel):
    """
    Modelo de dados para funcionário
    Representa as informações básicas de um funcionário no sistema
    """
    id: str
    name: Optional[str] = None
    email: Optional[str] = None
    department: Optional[str] = None
    has_photo: bool = False
    photo_path: Optional[str] = None
    encoding_path: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class FacialVerificationResult(BaseModel):
    """
    Resultado da verificação facial
    """
    employee_id: str
    verified: bool
    similarity: float  # Porcentagem de similaridade
    confidence: str    # high, medium, low
    timestamp: datetime
    
class FacialRegistrationResult(BaseModel):
    """
    Resultado do registro de foto facial
    """
    employee_id: str
    success: bool
    message: str
    photo_path: Optional[str] = None
    encoding_path: Optional[str] = None 