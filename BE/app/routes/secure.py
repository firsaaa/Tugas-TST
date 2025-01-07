from fastapi import APIRouter, Depends, HTTPException, Header, Query
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from datetime import date, datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import os
from app.models import Reservation, User, Seat
from app.database import get_db
from app.schemas import ReservationCreate, ReservationResponse

# Router
router = APIRouter()

# Konstanta
API_KEY = os.getenv("API_KEY")  # Ambil API Key dari .env
SECRET_KEY = os.getenv("SECRET_KEY", "fallback_secret_key")  # Secret Key untuk JWT
ALGORITHM = "HS256"  # Algoritma yang digunakan untuk JWT
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Durasi token

# OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Password Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Helper Functions
def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

# API Key Authentication
def api_key_auth(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return x_api_key

# Token Creation
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Token Validation
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Models
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class ReservationResponse(BaseModel):
    id: int
    user_name: str
    seat_number: str
    reservation_date: date
    created_at: datetime

    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    username: str
    password: str

# Endpoints

# Register User
@router.post("/register", summary="Register a new user")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already taken")

    hashed_password = hash_password(user.password)
    new_user = User(username=user.username, password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User registered successfully", "username": new_user.username}

# Login User
@router.post("/login", summary="Login user")
def login_user(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == request.username).first()
    if not user or not verify_password(request.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# Logout User
@router.post("/logout", summary="Logout user")
def logout_user(token: str = Depends(oauth2_scheme)):
    return {"message": "Logout successful"}

# Get User Details
@router.get("/users/{user_id}", summary="Get user details")
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"username": user.username, "created_at": user.created_at}

# Update User
@router.put("/users/{user_id}", summary="Update user")
def update_user(
    user_id: int,
    user_data: UserCreate,  # Expecting a Pydantic model for body
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)  # Validate Bearer token
):
    # Validate user existence
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update user data
    user.username = user_data.username
    user.password = hash_password(user_data.password)
    db.commit()
    return {"message": "User updated successfully"}

# Delete User
@router.delete("/users/{user_id}", summary="Delete user")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}

# Create Reservation

@router.post("/reservations", response_model=ReservationResponse)
def create_reservation(
    reservation: ReservationCreate, 
    db: Session = Depends(get_db),
    key: str = Depends(api_key_auth)
):
    # Check if a reservation already exists for the given seat and date
    existing_reservation = db.query(Reservation).filter(
        Reservation.seat_number == reservation.seat_number,
        Reservation.reservation_date == reservation.reservation_date
    ).first()

    if existing_reservation:
        raise HTTPException(
            status_code=400,
            detail="This seat is already reserved for the selected date."
        )

    # Create a new reservation if no conflicts exist
    db_reservation = Reservation(
        user_name=reservation.user_name,
        seat_number=reservation.seat_number,
        reservation_date=reservation.reservation_date,
    )
    db.add(db_reservation)
    db.commit()
    db.refresh(db_reservation)
    return db_reservation


@router.get("/reservations", summary="Get all reservations with optional filters")
def get_reservations(
    user_name: str = None,
    seat_number: str = None,
    reservation_date: str = None,
    db: Session = Depends(get_db),
    key: str = Depends(api_key_auth),
):
    query = db.query(Reservation)

    if user_name:
        query = query.filter(Reservation.user_name == user_name)
    if seat_number:
        query = query.filter(Reservation.seat_number == seat_number)
    if reservation_date:
        try:
            parsed_date = datetime.strptime(reservation_date, "%Y-%m-%d").date()
            query = query.filter(Reservation.reservation_date == parsed_date)
        except ValueError:
            raise HTTPException(status_code=422, detail="Invalid date format. Use YYYY-MM-DD")

    reservations = query.all()
    return reservations
    
@router.get("/seats")
def get_seats(db: Session = Depends(get_db)):
    seats = db.query(Seat).all()
    return [{"id": seat.id, "seat_number": seat.seat_number} for seat in seats]

# Check Seat Availability - Fixed endpoint
@router.get("/reservations/check-availability", summary="Check seat availability")
def check_seat_availability(
    seat_number: str = Query(..., description="Seat number to check"),
    reservation_date: str = Query(..., description="Reservation date in YYYY-MM-DD format"),
    db: Session = Depends(get_db),
    key: str = Depends(api_key_auth)
):
    try:
        parsed_date = datetime.strptime(reservation_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=422, 
            detail="Invalid date format. Use YYYY-MM-DD format"
        )
    
    reservation = db.query(Reservation).filter(
        Reservation.seat_number == seat_number,
        Reservation.reservation_date == parsed_date
    ).first()

    return {
        "available": not bool(reservation),
        "message": "Seat is available" if not reservation else "Seat is already reserved on this date"
    }

# Get Reservation by ID
@router.get("/reservations/{reservation_id}", summary="Get a reservation by ID")
def get_reservation(
    reservation_id: int, 
    db: Session = Depends(get_db), 
    key: str = Depends(api_key_auth)
):
    reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    return reservation

# Cancel/Delete Reservation - Combined the duplicate delete endpoints
@router.delete("/reservations/{reservation_id}", summary="Cancel/Delete a reservation")
def cancel_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    
    if reservation.user_name != current_user:
        raise HTTPException(status_code=403, detail="You can only cancel your own reservations")

    db.delete(reservation)
    db.commit()
    return {"message": "Reservation cancelled successfully"}
