from fastapi import APIRouter
import os

router = APIRouter()

@router.get("/")
def read_public():
    return {"message": "Welcome to Coworking Space API"}
