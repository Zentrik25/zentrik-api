"""
Provider ORM model - represents service providers in the system.
This model represents any business providing services:- Medical clinics- Real estate offices- Automotive repair shops- Salons/spas- Any front-desk business
The model is designed to be sector-agnostic and expandable.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from app.database import Base
class Provider(Base):
    """
    Provider entity - represents a service-providing business.
    This is a STATELESS model - it only defines the schema.
    No business logic or state management happens here.
    """
    __tablename__ = "providers"
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    # Core identification fields
    name = Column(String(255), nullable=False, index=True)  # Business name
    sector = Column(String(100), nullable=False, index=True)  # Industry: medical, real_estate, 
automotive, etc.
    # Contact information
    phone = Column(String(50), nullable=True)  # Phone number
    email = Column(String(255), nullable=True)  # Email address
    address = Column(Text, nullable=True)  # Physical address
    # Status tracking
    is_active = Column(Boolean, default=True, nullable=False)  # Whether provider is currently 
active
    # Audit timestamps - automatically managed
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)  # When record was 
created
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, 
nullable=False)  # Last update
    # Note: Relationship with bookings is defined via backref in Booking model
    # This avoids circular imports and keeps models independent