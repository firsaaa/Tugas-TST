from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import public, secure
from app.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root route
@app.get("/")
def read_root():
    return {"message": "Welcome to the Coworking Space API!"}

# Add other routes
app.include_router(public.router, prefix="/api/public", tags=["Public"])
app.include_router(secure.router, prefix="/api/secure", tags=["Secure"])