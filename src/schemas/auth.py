from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date, datetime
 
 
# ── Login ──────────────────────────────────────────────────────
 
class LoginRequest(BaseModel):
    email: EmailStr
    password: str
 
 
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
 
 
# ── Registro persona ───────────────────────────────────────────
 
class RegisterPersonaRequest(BaseModel):
    nombre_completo: str
    fecha_nacimiento: date
    biografia: Optional[str] = None
    ubicacion: str
    email: EmailStr
    password: str
 
 
# ── Registro empresa ───────────────────────────────────────────
 
class RegisterEmpresaRequest(BaseModel):
    nombre_negocio: str
    tipo_negocio: str
    descripcion_negocio: Optional[str] = None
    direccion: str
    telefono: str
    email: EmailStr
    password: str
 
 
# ── Respuesta pública del usuario ──────────────────────────────
 
class UsuarioOut(BaseModel):
    id: int
    tipo_cuenta: str
    email: str
    foto_perfil: Optional[str] = None
 
    # persona
    nombre_completo: Optional[str] = None
    ubicacion: Optional[str] = None
 
    # empresa
    nombre_negocio: Optional[str] = None
    tipo_negocio: Optional[str] = None
 
    class Config:
        from_attributes = True
        
class UsuarioOut(BaseModel):
    id: int
    tipo_cuenta: str
    email: str
    foto_perfil: Optional[str] = None

    # persona
    nombre_completo: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    biografia: Optional[str] = None
    ubicacion: Optional[str] = None

    # empresa
    nombre_negocio: Optional[str] = None
    tipo_negocio: Optional[str] = None
    descripcion_negocio: Optional[str] = None
    direccion: Optional[str] = None
    telefono: Optional[str] = None

    fecha_creacion: Optional[datetime] = None

    class Config:
        from_attributes = True