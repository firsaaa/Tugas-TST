from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routes import public, secure  # Pastikan ini di-load setelah Base didefinisikan
from app import models  # Impor models agar terdaftar di SQLAlchemy

# Buat tabel di database
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Ganti dengan URL frontend Anda di production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root route
@app.get("/")
def read_root():
    return {"message": "Welcome to the Coworking Space API!"}

# Tambahkan route lainnya
app.include_router(public.router, prefix="/api/public", tags=["Public"])
app.include_router(secure.router, prefix="/api/secure", tags=["Secure"])
