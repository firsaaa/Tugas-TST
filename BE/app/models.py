from sqlalchemy import Column, Integer, String, DateTime, Date
from sqlalchemy.sql import func
from app.database import Base

class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String, nullable=False)
    seat_number = Column(String, nullable=False)
    reservation_date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)

class Seat(Base):
    __tablename__ = "seats"

    id = Column(Integer, primary_key=True, index=True)
    seat_number = Column(String, unique=True, nullable=False)
