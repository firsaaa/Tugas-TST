from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def read_public():
    return {"message": "Welcome to Coworking Space API"}
