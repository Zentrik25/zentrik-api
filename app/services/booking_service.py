"""
Booking service - business logic layer for bookings.

This layer is STATELESS and contains ONLY business rules and validation.
NO database operations here - those are delegated to repositories.

Service layer responsibilities:
- Validate business rules (e.g., no past bookings, provider must exist)
- Coordinate between multiple repositories (provider + booking)
- Enforce business constraints
- Throw meaningful errors

This keeps business logic separate from data access and HTTP concerns.
"""
from typing import List, Optional
from datetime import datetime
from app.repositories.booking_repository import BookingRepository
from app.repositories.provider_repository import ProviderRepository
from app.schemas.booking import BookingCreate, BookingUpdate
from app.models.booking import BookingStatus


class BookingService:
    """
    Booking service - handles business logic for booking operations.
    
    IMPORTANT: This class is STATELESS.
    - Each instance receives repositories (which have sessions)
    - No state is stored between operations
    - All business rules are applied here
    """
    
    def __init__(self, booking_repo: BookingRepository, provider_repo: ProviderRepository):
        """
        Initialize service with repositories.
        
        Args:
            booking_repo: Booking repository for booking operations
            provider_repo: Provider repository to verify provider exists
        """
        self.booking_repo = booking_repo
        self.provider_repo = provider_repo

    def create_booking(self, data: BookingCreate):
        """
        Create a new booking with comprehensive business rule validation.
        
        Business rules enforced:
        1. Provider must exist in the system
        2. Provider must be active (not disabled)
        3. Scheduled time must be in the future
        
        Args:
            data: Validated booking data from API
            
        Returns:
            Created booking with PENDING status
            
        Raises:
            ValueError: If any business rule is violated
            
        Example:
            booking = service.create_booking(
                BookingCreate(
                    provider_id=1,
                    client_name="John Doe",
                    client_phone="+1234567890",
                    scheduled_at=datetime(2025, 1, 15, 10, 0)
                )
            )
        """
        # Business rule 1: Provider must exist
        provider = self.provider_repo.get_by_id(data.provider_id)
        if not provider:
            raise ValueError(f"Provider with ID {data.provider_id} not found")
        
        # Business rule 2: Provider must be active
        if not provider.is_active:
            raise ValueError(f"Provider is not active and cannot accept bookings")
        
        # Business rule 3: Cannot book in the past
        if data.scheduled_at < datetime.utcnow():
            raise ValueError("Scheduled time must be in the future")
        
        # All rules passed - create the booking
        return self.booking_repo.create(data)

    def get_booking(self, booking_id: int):
        """
        Get a booking by ID with existence validation.
        
        Args:
            booking_id: Booking's database ID
            
        Returns:
            Booking entity
            
        Raises:
            ValueError: If booking not found
        """
        booking = self.booking_repo.get_by_id(booking_id)
        if not booking:
            raise ValueError(f"Booking with ID {booking_id} not found")
        return booking

    def get_bookings(
        self,
        skip: int = 0,
        limit: int = 100,
        provider_id: Optional[int] = None,
        status: Optional[BookingStatus] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None
    ):
        """
        Get bookings with optional filtering.
        
        Args:
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
            provider_id: Filter by specific provider
            status: Filter by booking status
            from_date: Filter bookings scheduled after this date
            to_date: Filter bookings scheduled before this date
            
        Returns:
            List of bookings matching criteria
            
        Example:
            # Get all confirmed bookings for today
            today = datetime.now().replace(hour=0, minute=0, second=0)
            tomorrow = today + timedelta(days=1)
            bookings = service.get_bookings(
                status=BookingStatus.CONFIRMED,
                from_date=today,
                to_date=tomorrow
            )
        """
        return self.booking_repo.list_all(
            skip=skip,
            limit=limit,
            provider_id=provider_id,
            status=status,
            from_date=from_date,
            to_date=to_date
        )

    def update_booking(self, booking_id: int, data: BookingUpdate):
        """
        Update a booking with existence validation.
        
        Args:
            booking_id: Booking's database ID
            data: Fields to update
            
        Returns:
            Updated booking
            
        Raises:
            ValueError: If booking not found
            
        Note: Could add business rules here like:
        - Cannot reschedule a completed booking
        - Cannot confirm a cancelled booking
        - Must be within cancellation window
        """
        booking = self.booking_repo.update(booking_id, data)
        if not booking:
            raise ValueError(f"Booking with ID {booking_id} not found")
        return booking

    def cancel_booking(self, booking_id: int):
        """
        Cancel a booking by setting status to CANCELLED.
        
        This is preferred over deleting bookings as it maintains audit trail.
        
        Args:
            booking_id: Booking's database ID
            
        Returns:
            Cancelled booking
            
        Raises:
            ValueError: If booking not found
            
        Note: Could add business rules like:
        - Cannot cancel if within 24 hours
        - Cannot cancel already completed bookings
        - Notify provider of cancellation
        """
        update_data = BookingUpdate(status=BookingStatus.CANCELLED)
        return self.update_booking(booking_id, update_data)

    def delete_booking(self, booking_id: int):
        """
        Delete a booking permanently.
        
        Args:
            booking_id: Booking's database ID
            
        Returns:
            True if deleted
            
        Raises:
            ValueError: If booking not found
            
        WARNING: This is a hard delete. Consider using cancel_booking instead
        to maintain audit trail and history.
        
        In production, consider:
        - Only allow deletion if booking is pending
        - Require admin privileges
        - Archive data before deletion
        """
        success = self.booking_repo.delete(booking_id)
        if not success:
            raise ValueError(f"Booking with ID {booking_id} not found")
        return True