"""
Booking ORM model - represents appointments and reservations.

This model handles all types of bookings:
- Medical appointments
- Property viewings
- Service appointments
- Consultations
- Any time-based reservation

Status lifecycle: pending → confirmed → completed (or cancelled at any point)
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum
from app.database import Base


class BookingStatus(str, enum.Enum):
    """
    Booking status enum - represents the lifecycle of a booking.
    
    Status flow:
    1. PENDING - Initial state when booking is created
    2. CONFIRMED - Provider has confirmed the booking
    3. COMPLETED - Service has been delivered
    4. CANCELLED - Booking was cancelled (terminal state)
    """
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Booking(Base):
    """
    Booking entity - represents a scheduled appointment or reservation.
    
    This is a STATELESS model - it only defines the schema.
    All business logic is handled in the service layer.
    """
    __tablename__ = "bookings"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key to provider
    provider_id = Column(Integer, ForeignKey("providers.id"), nullable=False, index=True)
    
    # Client information - who is booking
    client_name = Column(String(255), nullable=False)  # Client's full name
    client_phone = Column(String(50), nullable=False)  # Client's phone (required for contact)
    client_email = Column(String(255), nullable=True)  # Client's email (optional)
    
    # Booking details - what and when
    service_type = Column(String(100), nullable=True)  # Type of service: "consultation", "viewing", "repair", etc.
    scheduled_at = Column(DateTime, nullable=False, index=True)  # When the appointment is scheduled
    status = Column(SQLEnum(BookingStatus), default=BookingStatus.PENDING, nullable=False, index=True)
    notes = Column(Text, nullable=True)  # Additional notes or special requests
    
    # Audit timestamps - automatically managed
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)  # When booking was created
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)  # Last update
    
    # Relationship to provider
    # backref creates a 'bookings' attribute on Provider model automatically
    # This is a ONE-TO-MANY relationship: one provider has many bookings
    provider = relationship("Provider", backref="bookings")