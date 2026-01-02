"""
Booking repository - data access layer for bookings.

This layer is STATELESS and handles ONLY database operations.
NO business logic here - just CRUD operations.

Repository pattern benefits:
- Separates database concerns from business logic
- Makes testing easier (can mock repository)
- Centralizes all database queries in one place
"""
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.booking import Booking, BookingStatus
from app.schemas.booking import BookingCreate, BookingUpdate


class BookingRepository:
    """
    Booking repository - handles all database operations for bookings.
    
    IMPORTANT: This class is STATELESS.
    - Each instance receives a fresh database session
    - No state is stored between operations
    - Thread-safe and concurrency-safe
    """
    
    def __init__(self, db: Session):
        """
        Initialize repository with database session.
        
        Args:
            db: SQLAlchemy session (will be closed by FastAPI after request)
        """
        self.db = db

    def create(self, data: BookingCreate) -> Booking:
        """
        Create a new booking in the database.
        
        Args:
            data: Validated booking data from API
            
        Returns:
            Created booking with auto-generated ID, timestamps, and PENDING status
            
        Note: Status is automatically set to PENDING on creation.
        """
        # Convert Pydantic schema to dict and create ORM model
        booking = Booking(**data.model_dump())
        
        # Add to session and commit
        self.db.add(booking)
        self.db.commit()  # Persist to database
        self.db.refresh(booking)  # Load generated fields
        
        return booking

    def get_by_id(self, booking_id: int) -> Optional[Booking]:
        """
        Retrieve a single booking by ID.
        
        Args:
            booking_id: Booking's database ID
            
        Returns:
            Booking if found, None otherwise
        """
        return self.db.query(Booking).filter(Booking.id == booking_id).first()

    def list_all(
        self, 
        skip: int = 0, 
        limit: int = 100,
        provider_id: Optional[int] = None,
        status: Optional[BookingStatus] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None
    ) -> List[Booking]:
        """
        List bookings with optional filtering and pagination.
        
        Args:
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
            provider_id: Filter by specific provider
            status: Filter by booking status (pending, confirmed, etc.)
            from_date: Filter bookings scheduled after this date
            to_date: Filter bookings scheduled before this date
            
        Returns:
            List of bookings matching criteria, ordered by scheduled time
            
        Example:
            # Get all confirmed bookings for provider 1 in January 2025
            bookings = repo.list_all(
                provider_id=1,
                status=BookingStatus.CONFIRMED,
                from_date=datetime(2025, 1, 1),
                to_date=datetime(2025, 1, 31)
            )
        """
        query = self.db.query(Booking)
        
        # Apply filters if provided
        if provider_id:
            query = query.filter(Booking.provider_id == provider_id)
        if status:
            query = query.filter(Booking.status == status)
        if from_date:
            query = query.filter(Booking.scheduled_at >= from_date)
        if to_date:
            query = query.filter(Booking.scheduled_at <= to_date)
        
        # Order by scheduled time (earliest first) and apply pagination
        return query.order_by(Booking.scheduled_at).offset(skip).limit(limit).all()

    def update(self, booking_id: int, data: BookingUpdate) -> Optional[Booking]:
        """
        Update an existing booking.
        
        Args:
            booking_id: Booking's database ID
            data: Fields to update (only provided fields are updated)
            
        Returns:
            Updated booking if found, None otherwise
            
        Note: This uses PATCH semantics - only provided fields are updated.
        Common use cases:
        - Reschedule: update scheduled_at
        - Confirm: update status to CONFIRMED
        - Update contact: update client_phone or client_email
        """
        # Find booking
        booking = self.get_by_id(booking_id)
        if not booking:
            return None
        
        # Get only the fields that were actually provided in the request
        update_data = data.model_dump(exclude_unset=True)
        
        # Update each provided field
        for field, value in update_data.items():
            setattr(booking, field, value)
        
        # Commit changes (updated_at is automatically updated)
        self.db.commit()
        self.db.refresh(booking)
        
        return booking

    def delete(self, booking_id: int) -> bool:
        """
        Delete a booking from the database.
        
        Args:
            booking_id: Booking's database ID
            
        Returns:
            True if deleted, False if not found
            
        WARNING: This is a hard delete. Consider using cancel_booking 
        (set status to CANCELLED) instead for audit trail.
        """
        booking = self.get_by_id(booking_id)
        if not booking:
            return False
        
        # Delete and commit
        self.db.delete(booking)
        self.db.commit()
        
        return True