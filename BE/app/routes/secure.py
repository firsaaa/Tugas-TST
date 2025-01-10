from fastapi import APIRouter, Depends, HTTPException, Header, Query, Body, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from datetime import date, datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import os
from app.models import Reservation, User, Seat
from app.database import get_db
from app.schemas import ReservationCreate, ReservationResponse, MediMatch
import requests
from typing import List, Optional

# Router
router = APIRouter()

# Konstanta
API_KEY = os.getenv("API_KEY")  # Ambil API Key dari .env
SECRET_KEY = os.getenv("SECRET_KEY", "fallback_secret_key")  # Secret Key untuk JWT
ALGORITHM = "HS256"  # Algoritma yang digunakan untuk JWT
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # Durasi token

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

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenRefresh(BaseModel):
    refresh_token: str

def create_refresh_token(user_id: str) -> str:
    token = os.urandom(16).hex()  # Generate a random token
    refresh_token_store[token] = user_id
    return token

# Refresh Token
refresh_token_store = {}

@router.post("/refresh-token", response_model=TokenResponse)
async def refresh_token(
    token_data: TokenRefresh,
    x_api_key: Optional[str] = Header(None)
):
    # First check API key if provided
    if x_api_key:
        if x_api_key != API_KEY:
            raise HTTPException(status_code=403, detail="Invalid API Key")
    
    # Verify refresh token
    user_id = refresh_token_store.get(token_data.refresh_token)
    if not user_id:
        raise HTTPException(status_code=403, detail="Invalid refresh token")
    
    # Create new tokens
    new_access_token = create_access_token(data={"sub": user_id})
    new_refresh_token = create_refresh_token(user_id)
    
    # Remove old refresh token
    refresh_token_store.pop(token_data.refresh_token, None)
    
    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token
    )


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

#firebase
import requests
from fastapi import APIRouter, HTTPException, Query
from starlette.responses import JSONResponse

router = APIRouter()

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
    refresh_token = create_refresh_token(user.username)
    return {"access_token": access_token, "refresh_token": refresh_token,"token_type": "bearer"}

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
    current_user: str = Depends(get_current_user)  # Get user from token
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
        user_name=current_user,  # Get the username from the token
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
    current_user: str = Depends(get_current_user),
):
    query = db.query(Reservation)

    if not user_name:
        query = query.filter(Reservation.user_name == current_user)
    else: 
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

@router.get("/verify-token", summary="Verify token")
def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"username": username, "valid": True}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    
@router.get("/seats")
def get_seats(db: Session = Depends(get_db)):
    seats = db.query(Seat).all()
    return [{"id": seat.id, "seat_number": seat.seat_number} for seat in seats]

# Check Seat Availability - Fixed endpoint
@router.get("/reservations/check-availability")
def check_seat_availability(
    seat_number: str = Query(..., description="Seat number to check"),
    reservation_date: str = Query(..., description="Reservation date in YYYY-MM-DD format"),
    db: Session = Depends(get_db),
    key: str = Depends(api_key_auth)
):
    try:
        parsed_date = datetime.strptime(reservation_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid date format. Use YYYY-MM-DD")
    
    reservation = db.query(Reservation).filter(
        Reservation.seat_number == seat_number,
        Reservation.reservation_date == parsed_date
    ).first()

    return {
        "available": not bool(reservation),
        "message": "Seat is available" if not reservation else "Seat is already reserved"
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

@router.get("/proxy/check-availability", summary="Proxy for Check Availability")
def proxy_check_availability(
    seat_number: str = Query(..., description="Seat number"),
    reservation_date: str = Query(..., description="Reservation date (YYYY-MM-DD)"),
):
    api_url = f"https://coworkingspace.up.railway.app/api/secure/reservations/check-availability?seat_number={seat_number}&reservation_date={reservation_date}"
    
    headers = {
        "x-api-key": os.getenv("API_KEY"),  # Pastikan API_KEY ada di environment
    }

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()  # Raise HTTPError jika status bukan 200
    except requests.RequestException as e:
        raise HTTPException(status_code=response.status_code, detail=str(e))
    
    return JSONResponse(content=response.json())

@router.get("/my-reservations", response_model=List[ReservationResponse])
async def get_my_reservations(user_id: str):
    reservations = await ReservationModel.find({"user_id": user_id}).to_list()
    current_date = datetime.now()

    for reservation in reservations:
        reservation_date = datetime.strptime(reservation["reservation_date"], "%Y-%m-%d")
        if reservation_date < current_date:
            reservation["status"] = "done"
        else:
            reservation["status"] = "active"

    return JSONResponse(content={"data": reservations})


#Integrasi dengan MediMatch
MEDIMATCH_API_KEY = os.getenv("MEDIMATCH_API_KEY")
MEDIMATCH_URL = "https://backend.medimatch.web.id/recommend"

@router.post("/recommend-drugs", summary="Recommend Drugs from Friend's API")
async def recommend_drugs(
    request: Request,
    drug_name: str = Body(..., embed=True, description="Name of the drug to find alternatives for"),
    top_n: int = Body(5, embed=True, description="Number of recommendations to retrieve")
):
    # Get the API key from headers using the correct header name
    api_key = request.headers.get("api-key")
    if not api_key:
        raise HTTPException(status_code=403, detail="Missing API key")
    
    # Verify our API key
    if api_key != MEDIMATCH_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    
    payload = {
        "drug_name": drug_name,
        "top_n": top_n
    }
    
    # Use the correct header name for the MediMatch API
    headers = {
        "api-key": api_key,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(MEDIMATCH_URL, json=payload, headers=headers)

        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        if exc.response is not None:
            status_code = exc.response.status_code
            try:
                error_detail = exc.response.json()
                raise HTTPException(status_code=status_code, detail=error_detail)
            except ValueError:
                raise HTTPException(status_code=status_code, detail=str(exc))
        raise HTTPException(status_code=500, detail=str(exc))
