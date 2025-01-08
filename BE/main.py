from fastapi import FastAPI, Query, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.routes import public, secure
from app.database import Base, engine
from dotenv import load_dotenv
import requests
import os

load_dotenv()

app = FastAPI()

# Handle database creation
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Database initialization error: {e}")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",  
        "https://coworkingspace-backend.vercel.app"  
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root route
@app.get("/")
def read_root():
    return {"message": "Welcome to the Coworking Space API!"}

@router.get("/proxy/check-availability", summary="Proxy endpoint for availability")
def proxy_check_availability(
    seat_number: str,
    reservation_date: str,
    db: Session = Depends(get_db),
):
    api_url = f"https://coworkingspace-backend.vercel.app/api/secure/reservations/check-availability?seat_number={seat_number}&reservation_date={reservation_date}"
    headers = {
        "x-api-key": os.getenv("API_KEY"),  # Ambil API key dari environment
        "Authorization": "Bearer <token>",  # Ganti jika autentikasi token diperlukan
    }

    response = requests.get(api_url, headers=headers)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.json())
    return response.json()

# Tambahkan route lainnya
app.include_router(public.router, prefix="/api/public", tags=["Public"])
app.include_router(secure.router, prefix="/api/secure", tags=["Secure"])
app.include_router(public.router)


