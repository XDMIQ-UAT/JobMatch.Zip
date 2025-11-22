from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://jobmatch:password@localhost:5432/jobmatch"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Import models after Base is defined
from .profile import AnonymousProfile
from .assessment import Assessment
from .match import Match

__all__ = ["Base", "SessionLocal", "engine", "AnonymousProfile", "Assessment", "Match"]
