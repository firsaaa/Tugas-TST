from fastapi import APIRouter
import os

router = APIRouter()

@router.get("/debug")
def debug_env():
    return {
        "DATABASE_URL": os.getenv("DATABASE_URL"),
        "API_KEY": os.getenv("API_KEY"),
        "SECRET_KEY": os.getenv("SECRET_KEY")
    }

@router.get("/")
def read_public():
    return {"message": "Welcome to Coworking Space API"}
