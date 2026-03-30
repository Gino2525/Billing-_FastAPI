from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

DATABASE_URL = os.getenv("DATABASE_URL")

# If DATABASE_URL exists → use PostgreSQL (Render)
if DATABASE_URL:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True
    )

# Else → use SQLite (Local development)
else:
    BASE_DIR = os.getcwd()
    db_path = os.path.join(BASE_DIR, "billing.db")

    print("Using Local DB at:", db_path)

    DATABASE_URL = f"sqlite:///{db_path}"

    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

Base = declarative_base()