from sqlalchemy import Column, Integer, String, Boolean, Text, Date, DateTime, Enum
from sqlalchemy.sql import func
from src.database import Base
import enum


class TipoCuenta(str, enum.Enum):
    persona = "persona"
    empresa = "empresa"


class TipoNegocio(str, enum.Enum):
    restaurante = "restaurante"
    tienda = "tienda"
    servicio = "servicio"
    tecnologia = "tecnologia"
    educacion = "educacion"
    salud = "salud"
    moda = "moda"
    entretenimiento = "entretenimiento"
    otro = "otro"


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    tipo_cuenta = Column(Enum(TipoCuenta), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(Text, nullable=False)
    foto_perfil = Column(String(255), nullable=True)
    activo = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime, server_default=func.now())
    ultimo_login = Column(DateTime, nullable=True)

    # Campos persona
    nombre_completo = Column(String(150), nullable=True)
    fecha_nacimiento = Column(Date, nullable=True)
    biografia = Column(Text, nullable=True)
    ubicacion = Column(String(150), nullable=True)

    # Campos empresa
    nombre_negocio = Column(String(150), nullable=True)
    tipo_negocio = Column(Enum(TipoNegocio), nullable=True)
    descripcion_negocio = Column(Text, nullable=True)
    direccion = Column(String(255), nullable=True)
    telefono = Column(String(30), nullable=True)