import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from src.routers.auth import router as auth_router
from src.config import settings
from src.database import create_tables
 
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)
 
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
 
@app.on_event("startup")
def on_startup():
    create_tables()
 
# Fotos de perfil accesibles en /uploads/profile_photos/<filename>
os.makedirs("uploads/profile_photos", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
 
app.include_router(auth_router, prefix="/api/v1")  # ← agregar prefix aquí
 
@app.get("/health")
def health():
    return {"status": "ok", "service": settings.APP_NAME}