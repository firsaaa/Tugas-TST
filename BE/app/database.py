from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set. Check your .env file.")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True, 
    connect_args={"sslmode": "require"}  
)

# Session dan Base untuk ORM
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency untuk mendapatkan session database
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
