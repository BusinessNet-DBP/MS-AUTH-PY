from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.database import SessionLocal
from src.models.usuario import Usuario
from src.schemas.auth import LoginRequest, TokenResponse
from src.utils.security import verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):

    user = db.query(Usuario).filter(Usuario.email == data.email).first()

    if not user:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")

    if not user.activo:
        raise HTTPException(status_code=403, detail="Usuario inactivo")

    if not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Contraseña incorrecta")

    token = create_access_token({
        "sub": str(user.id),
        "email": user.email
    })

    return {
        "access_token": token
    }