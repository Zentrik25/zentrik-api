"""
Database configuration and connection management.
This module is STATELESS - no session state is maintained.
Each request gets a fresh database session that is automatically closed.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()
# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", 
"postgresql://booking_user:booking_pass@localhost:5432/booking_db")
# Create engine with connection pooling
# pool_pre_ping=True ensures connections are valid before use
# echo=True logs all SQL statements (disable in production)
engine = create_engine(
    DATABASE_URL, 
    echo=True,  # Set to False in production
    pool_pre_ping=True,  # Validates connections before using them
    pool_size=5,  # Number of connections to maintain
    max_overflow=10  # Maximum overflow connections
)
# Session factory - creates new sessions when called
# autocommit=False: we control when to commit
# autoflush=False: we control when to flush changes
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
# Base class for all ORM models
Base = declarative_base()
def get_db():
    """
    Database session dependency for FastAPI.
    CRITICAL: This is STATELESS.
    - Each request gets a NEW database session
    - Session is automatically closed after request completes
    - No session state persists between requests
    - Thread-safe and concurrency-safe
    Usage in routes:
        def my_route(db: Session = Depends(get_db)):
            # Use db here
            pass
    """
    db = SessionLocal()  # Create new session
    try:
        yield db  # Provide session to request handler
    finally:
        db.close()  # ALWAYS close session, even if error occurs
def init_db():
    """
    Initialize database tables.
    WARNING: Only use this in development.
    In production, use Alembic migrations instead.
    This creates all tables defined in models if they don't exist.
    """
    Base.metadata.create_all(bind=engine)