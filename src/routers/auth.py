import os
import re
import shutil
import uuid
from datetime import datetime, date

from fastapi import APIRouter, Depends, HTTPException, Form, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
from jose import jwt, JWTError

from src.database import SessionLocal
from src.models.usuario import Usuario, TipoCuenta, TipoNegocio
from src.schemas.auth import LoginRequest, TokenResponse, UsuarioOut
from src.utils.security import verify_password, hash_password, create_access_token
from src.config import settings

router = APIRouter(prefix="/auth", tags=["Auth"])

UPLOAD_DIR = "uploads/profile_photos"
os.makedirs(UPLOAD_DIR, exist_ok=True)

security = HTTPBearer()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def save_photo(photo: UploadFile) -> str:
    ext = os.path.splitext(photo.filename)[-1].lower()
    filename = f"{uuid.uuid4()}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    with open(filepath, "wb") as f:
        shutil.copyfileobj(photo.file, f)
    return filepath


def validar_password(password: str):
    errores = []
    if len(password) < 8:
        errores.append("mínimo 8 caracteres")
    if not re.search(r'[a-z]', password):
        errores.append("al menos una minúscula")
    if not re.search(r'[A-Z]', password):
        errores.append("al menos una mayúscula")
    if not re.search(r'\d', password):
        errores.append("al menos un número")
    if errores:
        raise HTTPException(status_code=422, detail=f"La contraseña debe tener: {', '.join(errores)}")


def validar_edad(fecha_nacimiento: date):
    today = date.today()
    age = today.year - fecha_nacimiento.year
    if (today.month, today.day) < (fecha_nacimiento.month, fecha_nacimiento.day):
        age -= 1
    if age < 18:
        raise HTTPException(status_code=422, detail="Debes ser mayor de edad para registrarte")


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> Usuario:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Token inválido")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

    user = db.query(Usuario).filter(Usuario.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    if not user.activo:
        raise HTTPException(status_code=403, detail="Usuario inactivo")
    return user


# ── LOGIN ──────────────────────────────────────────────────────

@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(Usuario).filter(Usuario.email == data.email).first()

    if not user:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    if not user.activo:
        raise HTTPException(status_code=403, detail="Usuario inactivo")
    if not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Contraseña incorrecta")

    user.ultimo_login = datetime.utcnow()
    db.commit()

    token = create_access_token({
        "sub": str(user.id),
        "email": user.email,
        "tipo_cuenta": user.tipo_cuenta,
    })
    return {"access_token": token}


# ── ME ─────────────────────────────────────────────────────────

@router.get("/me", response_model=UsuarioOut)
def me(current_user: Usuario = Depends(get_current_user)):
    return current_user


# ── REGISTRO PERSONA ───────────────────────────────────────────

@router.post("/register/persona", response_model=TokenResponse, status_code=201)
async def register_persona(
    nombre_completo: str = Form(...),
    fecha_nacimiento: date = Form(...),
    ubicacion: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    biografia: Optional[str] = Form(None),
    foto_perfil: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
):
    if db.query(Usuario).filter(Usuario.email == email).first():
        raise HTTPException(status_code=409, detail="El correo ya está registrado")

    validar_password(password)
    validar_edad(fecha_nacimiento)

    foto_path = save_photo(foto_perfil) if foto_perfil and foto_perfil.filename else None

    usuario = Usuario(
        tipo_cuenta=TipoCuenta.persona,
        email=email,
        password_hash=hash_password(password),
        foto_perfil=foto_path,
        nombre_completo=nombre_completo,
        fecha_nacimiento=fecha_nacimiento,
        biografia=biografia,
        ubicacion=ubicacion,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    token = create_access_token({
        "sub": str(usuario.id),
        "email": usuario.email,
        "tipo_cuenta": usuario.tipo_cuenta,
    })
    return {"access_token": token}


# ── REGISTRO EMPRESA ───────────────────────────────────────────

@router.post("/register/empresa", response_model=TokenResponse, status_code=201)
async def register_empresa(
    nombre_negocio: str = Form(...),
    tipo_negocio: str = Form(...),
    direccion: str = Form(...),
    telefono: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    descripcion_negocio: Optional[str] = Form(None),
    foto_perfil: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
):
    if db.query(Usuario).filter(Usuario.email == email).first():
        raise HTTPException(status_code=409, detail="El correo ya está registrado")

    validar_password(password)

    try:
        tipo = TipoNegocio(tipo_negocio)
    except ValueError:
        raise HTTPException(status_code=422, detail=f"Tipo de negocio inválido: {tipo_negocio}")

    foto_path = save_photo(foto_perfil) if foto_perfil and foto_perfil.filename else None

    usuario = Usuario(
        tipo_cuenta=TipoCuenta.empresa,
        email=email,
        password_hash=hash_password(password),
        foto_perfil=foto_path,
        nombre_negocio=nombre_negocio,
        tipo_negocio=tipo,
        descripcion_negocio=descripcion_negocio,
        direccion=direccion,
        telefono=telefono,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    token = create_access_token({
        "sub": str(usuario.id),
        "email": usuario.email,
        "tipo_cuenta": usuario.tipo_cuenta,
    })
    return {"access_token": token}


# ── VER PERFIL DE CUALQUIER USUARIO ────────────────────────────

@router.get("/users/{user_id}", response_model=UsuarioOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(Usuario).filter(Usuario.id == user_id, Usuario.activo == True).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user


# ── EDITAR MI PERFIL ────────────────────────────────────────────

@router.put("/me", response_model=UsuarioOut)
async def update_me(
    nombre_completo: Optional[str] = Form(None),
    fecha_nacimiento: Optional[date] = Form(None),
    biografia: Optional[str] = Form(None),
    ubicacion: Optional[str] = Form(None),
    nombre_negocio: Optional[str] = Form(None),
    tipo_negocio: Optional[str] = Form(None),
    descripcion_negocio: Optional[str] = Form(None),
    direccion: Optional[str] = Form(None),
    telefono: Optional[str] = Form(None),
    foto_perfil: Optional[UploadFile] = File(None),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if foto_perfil and foto_perfil.filename:
        if current_user.foto_perfil and os.path.exists(current_user.foto_perfil):
            os.remove(current_user.foto_perfil)
        current_user.foto_perfil = save_photo(foto_perfil)

    if nombre_completo is not None:     current_user.nombre_completo = nombre_completo
    if fecha_nacimiento is not None:    current_user.fecha_nacimiento = fecha_nacimiento
    if biografia is not None:           current_user.biografia = biografia
    if ubicacion is not None:           current_user.ubicacion = ubicacion
    if nombre_negocio is not None:      current_user.nombre_negocio = nombre_negocio
    if descripcion_negocio is not None: current_user.descripcion_negocio = descripcion_negocio
    if direccion is not None:           current_user.direccion = direccion
    if telefono is not None:            current_user.telefono = telefono

    if tipo_negocio is not None:
        try:
            current_user.tipo_negocio = TipoNegocio(tipo_negocio)
        except ValueError:
            raise HTTPException(status_code=422, detail=f"Tipo de negocio inválido: {tipo_negocio}")

    db.commit()
    db.refresh(current_user)
    return current_user