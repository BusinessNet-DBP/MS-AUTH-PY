from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.routers.auth import router as auth_router

app = FastAPI(title="MS AUTH")

# Orígenes permitidos (tu frontend)
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000"  # opcional, por si accedes con 127.0.0.1
]

# Middleware de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],      # dominios que pueden hacer requests
    allow_credentials=True,     # cookies y credenciales
    allow_methods=["*"],        # GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],        # headers permitidos
)

# Routers
app.include_router(auth_router)