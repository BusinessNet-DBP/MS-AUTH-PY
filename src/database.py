from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from src.config import settings
 
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,       # reconecta si la conexión cae
    pool_size=5,
    max_overflow=10,
)
 
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
 
Base = declarative_base()
 
 
def create_tables():
    """Crea todas las tablas si no existen. Llamado al iniciar la app."""
    from src.models.usuario import Usuario  # noqa: F401 — importar para que Base las registre
    Base.metadata.create_all(bind=engine)