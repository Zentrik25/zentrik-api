"""
Booking API routes - HTTP layer for booking operations.

This layer is STATELESS and handles ONLY HTTP concerns:
- Request parsing and validation (handled by FastAPI/Pydantic)
- Response formatting
- HTTP status codes
- Error handling

NO business logic here - that's in the service layer.
NO database operations here - that's in the repository layer.

Each request gets a fresh database session via dependency injection.
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.booking import BookingCreate, BookingUpdate, BookingRead
from app.repositories.booking_repository import BookingRepository
from app.repositories.provider_repository import ProviderRepository
from app.services.booking_service import BookingService
from app.models.booking import BookingStatus

# Create router with prefix and tags for API documentation
router = APIRouter(prefix="/bookings", tags=["Bookings"])


def get_booking_service(db: Session = Depends(get_db)) -> BookingService:
    """
    Dependency injection for booking service.
    
    CRITICAL: This is STATELESS.
    - Each request gets a NEW database session via get_db()
    - New repository and service instances are created per request
    - No state persists between requests
    - Session is automatically closed by FastAPI after request
    
    Args:
        db: Database session (injected by FastAPI)
        
    Returns:
        Configured BookingService ready to use
    """
    booking_repo = BookingRepository(db)
    provider_repo = ProviderRepository(db)
    return BookingService(booking_repo, provider_repo)


@router.post("/", response_model=BookingRead, status_code=201)
def create_booking(
    payload: BookingCreate,
    service: BookingService = Depends(get_booking_service)
):
    """
    Create a new booking.
    
    Business rules enforced:
    - Provider must exist and be active
    - Scheduled time must be in the future
    - Initial status is automatically set to PENDING
    
    Args:
        payload: Booking data (validated by Pydantic)
        service: Booking service (injected by FastAPI)
        
    Returns:
        Created booking with HTTP 201 status
        
    Raises:
        HTTPException 400: If business rules are violated
        
    Example request body:
        {
            "provider_id": 1,
            "client_name": "John Doe",
            "client_phone": "+1234567890",
            "client_email": "john@example.com",
            "service_type": "consultation",
            "scheduled_at": "2025-01-15T10:00:00",
            "notes": "First visit"
        }
    """
    try:
        return service.create_booking(payload)
    except ValueError as e:
        # Convert business rule violations to HTTP 400 Bad Request
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[BookingRead])
def list_bookings(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum records to return"),
    provider_id: Optional[int] = Query(None, description="Filter by provider ID"),
    status: Optional[BookingStatus] = Query(None, description="Filter by status (pending, confirmed, completed, cancelled)"),
    from_date: Optional[datetime] = Query(None, description="Filter bookings scheduled after this date (ISO 8601)"),
    to_date: Optional[datetime] = Query(None, description="Filter bookings scheduled before this date (ISO 8601)"),
    service: BookingService = Depends(get_booking_service)
):
    """
    List bookings with optional filtering and pagination.
    
    Query parameters:
        - skip: Number of records to skip (default: 0)
        - limit: Max records to return (default: 100, max: 100)
        - provider_id: Filter by specific provider (optional)
        - status: Filter by booking status (optional)
        - from_date: Start date for date range filter (optional)
        - to_date: End date for date range filter (optional)
        
    Returns:
        List of bookings matching criteria, ordered by scheduled time
        
    Examples:
        GET /bookings?provider_id=1
        GET /bookings?status=confirmed
        GET /bookings?from_date=2025-01-01T00:00:00&to_date=2025-01-31T23:59:59
        GET /bookings?provider_id=1&status=pending&limit=10
    """
    return service.get_bookings(
        skip=skip,
        limit=limit,
        provider_id=provider_id,
        status=status,
        from_date=from_date,
        to_date=to_date
    )


@router.get("/{booking_id}", response_model=BookingRead)
def get_booking(
    booking_id: int,
    service: BookingService = Depends(get_booking_service)
):
    """
    Get a specific booking by ID.
    
    Args:
        booking_id: Booking's database ID (from URL path)
        service: Booking service (injected by FastAPI)
        
    Returns:
        Booking details
        
    Raises:
        HTTPException 404: If booking not found
        
    Example:
        GET /bookings/1
    """
    try:
        return service.get_booking(booking_id)
    except ValueError as e:
        # Convert "not found" errors to HTTP 404
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/{booking_id}", response_model=BookingRead)
def update_booking(
    booking_id: int,
    payload: BookingUpdate,
    service: BookingService = Depends(get_booking_service)
):
    """
    Update a booking (partial update using PATCH semantics).
    
    Only provided fields will be updated. Omitted fields remain unchanged.
    
    Common use cases:
    - Reschedule: update scheduled_at
    - Confirm: update status to "confirmed"
    - Update contact: update client_phone or client_email
    - Complete: update status to "completed"
    
    Args:
        booking_id: Booking's database ID (from URL path)
        payload: Fields to update (validated by Pydantic)
        service: Booking service (injected by FastAPI)
        
    Returns:
        Updated booking
        
    Raises:
        HTTPException 404: If booking not found
        
    Example request body (all fields optional):
        {
            "scheduled_at": "2025-01-16T14:00:00",
            "status": "confirmed"
        }
    """
    try:
        return service.update_booking(booking_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{booking_id}/cancel", response_model=BookingRead)
def cancel_booking(
    booking_id: int,
    service: BookingService = Depends(get_booking_service)
):
    """
    Cancel a booking by setting status to CANCELLED.
    
    This is a convenience endpoint that's equivalent to:
    PATCH /bookings/{id} with {"status": "cancelled"}
    
    Preferred over DELETE as it maintains audit trail.
    
    Args:
        booking_id: Booking's database ID (from URL path)
        service: Booking service (injected by FastAPI)
        
    Returns:
        Cancelled booking
        
    Raises:
        HTTPException 404: If booking not found
        
    Example:
        POST /bookings/1/cancel
    """
    try:
        return service.cancel_booking(booking_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{booking_id}", status_code=204)
def delete_booking(
    booking_id: int,
    service: BookingService = Depends(get_booking_service)
):
    """
    Delete a booking permanently.
    
    WARNING: This is a hard delete. Consider using POST /bookings/{id}/cancel
    instead to maintain audit trail.
    
    Args:
        booking_id: Booking's database ID (from URL path)
        service: Booking service (injected by FastAPI)
        
    Returns:
        HTTP 204 No Content (successful deletion returns no body)
        
    Raises:
        HTTPException 404: If booking not found
        
    Example:
        DELETE /bookings/1
    """
    try:
        service.delete_booking(booking_id)
        # No return value - HTTP 204 means "success, no content"
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))