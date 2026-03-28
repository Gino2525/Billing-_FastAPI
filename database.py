from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Store DB in same folder where EXE runs
BASE_DIR = os.getcwd()
db_path = os.path.join(BASE_DIR, "billing.db")

print("Using DB at:", db_path)

DATABASE_URL = f"sqlite:///{db_path}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()