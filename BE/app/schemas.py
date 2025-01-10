# schemas.py
from pydantic import BaseModel, EmailStr
from datetime import date, datetime

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(BaseModel):
    username: str
    email: EmailStr

    class Config:
        from_attributes = True

class ReservationCreate(BaseModel):
    seat_number: str
    reservation_date: date

class ReservationResponse(BaseModel):
    id: int
    user_name: str
    seat_number: str
    reservation_date: date
    created_at: datetime

    class Config:
        from_attributes = True

class MediMatch(BaseModel):
    drug_name: str
    top_n: int
