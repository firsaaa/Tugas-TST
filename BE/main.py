from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import public, secure
from app.database import Base, engine
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()
firebase_api_key = os.getenv("FIREBASE_API_KEY")

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
        "https://coworkingspace-six.vercel.app",
        "https://coworkingspace-backend.vercel.app",
        "https://coworkingspace.up.railway.app",
        "https://www.api.picacoworkingspace.site",
        "https://picacoworkingspace.site" \
    ],
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
app.include_router(public.router)


