from fastapi import FastAPI
from app.routes import public, secure
from app.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()

# Rute utama
@app.get("/")
def read_root():
    return {"message": "Welcome to the Coworking Space API!"}

# Tambahkan rute lain
app.include_router(public.router, prefix="/api/public", tags=["Public"])
app.include_router(secure.router, prefix="/api/secure", tags=["Secure"])
