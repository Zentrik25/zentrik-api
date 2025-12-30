"""
Booking Pydantic schemas - define API contracts for bookings.
These schemas are STATELESS and only handle validation.
They define what data comes in and goes out of the API.
Schema types:- Base: Common fields shared across schemas- Create: Required fields for creating a booking- Update: Optional fields for updating a booking- Read: Complete booking data returned to client
"""
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from app.models.booking import BookingStatus
class BookingBase(BaseModel):
    """
    Base schema with common booking fields.
    Used as parent for other booking schemas.
    """
    provider_id: int = Field(..., description="ID of the provider offering the service")
    client_name: str = Field(..., min_length=1, max_length=255, description="Client's full 
name")
    client_phone: str = Field(..., min_length=1, max_length=50, description="Client's contact 
phone")
    client_email: Optional[EmailStr] = Field(None, description="Client's email (optional)")
    service_type: Optional[str] = Field(None, max_length=100, description="Type of service being 
booked")
    scheduled_at: datetime = Field(..., description="When the appointment is scheduled (ISO 8601 
format)")
    notes: Optional[str] = Field(None, description="Additional notes or special requests")
class BookingCreate(BookingBase):
    """
    Schema for creating a new booking.
    Inherits all required fields from BookingBase.
    Required fields: provider_id, client_name, client_phone, scheduled_at
    Optional fields: client_email, service_type, notes
    Status is automatically set to PENDING on creation.
    """
    pass
class BookingUpdate(BaseModel):
    """
    Schema for updating an existing booking.
    ALL fields are optional - only provided fields will be updated.
    This allows partial updates (PATCH semantics).
    Clients can update individual fields without sending entire booking.
    """
    client_name: Optional[str] = Field(None, min_length=1, max_length=255, description="Updated 
client name")
    client_phone: Optional[str] = Field(None, min_length=1, max_length=50, description="Updated 
phone")
    client_email: Optional[EmailStr] = Field(None, description="Updated email")
    service_type: Optional[str] = Field(None, max_length=100, description="Updated service 
type")
    scheduled_at: Optional[datetime] = Field(None, description="Rescheduled time")
    status: Optional[BookingStatus] = Field(None, description="Updated status")
    notes: Optional[str] = Field(None, description="Updated notes")
class BookingRead(BookingBase):
    """
    Schema for reading booking data (API response).
    Includes all fields including auto-generated ones.
    This is what clients receive when they query bookings.
    """
    id: int  # Database ID
    status: BookingStatus  # Current booking status
    created_at: datetime  # When booking was created
    updated_at: datetime  # Last time booking was updated
    class Config:
        """
        Pydantic configuration.
        from_attributes=True allows creating this schema from ORM models.
        """
        from_attributes = True