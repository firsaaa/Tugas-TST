from fastapi import FastAPI
from app.routes import public, secure
from app.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


# Rute utama
@app.get("/")
def read_root():
    return {"message": "Welcome to the Coworking Space API!"}

# Tambahkan rute lain
app.include_router(public.router, prefix="/api/public", tags=["Public"])
app.include_router(secure.router, prefix="/api/secure", tags=["Secure"])
