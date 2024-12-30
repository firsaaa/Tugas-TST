from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
import logging

# Load environment variables
load_dotenv()


logging.basicConfig(level=logging.INFO)
logging.info(f"Connecting to database: {os.getenv('DATABASE_URL')}")

engine = create_engine(
    os.getenv("DATABASE_URL"),
    connect_args={"sslmode": "require"}  
)

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set. Check your .env file.")

# Session and Base for ORM
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency for database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
