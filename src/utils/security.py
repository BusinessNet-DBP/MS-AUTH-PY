from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from src.config import settings

# Contexto de hashing con bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # 1 hora

# Limite de bcrypt
MAX_BCRYPT_LENGTH = 72  # bcrypt solo acepta hasta 72 bytes

# ================================
# Funciones de seguridad
# ================================

def hash_password(password: str) -> str:
    """
    Hashea una contraseña aplicando truncamiento a 72 bytes
    """
    pwd_to_hash = password[:MAX_BCRYPT_LENGTH]
    return pwd_context.hash(pwd_to_hash)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica una contraseña aplicando truncamiento a 72 bytes
    """
    pwd_to_verify = plain_password[:MAX_BCRYPT_LENGTH]
    return pwd_context.verify(pwd_to_verify, hashed_password)

def create_access_token(data: dict) -> str:
    """
    Crea un token JWT con expiración de ACCESS_TOKEN_EXPIRE_MINUTES
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)