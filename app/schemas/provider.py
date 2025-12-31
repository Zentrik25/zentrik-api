"""
Provider Pydantic schemas - define API contracts for providers.

These schemas are STATELESS and only handle validation.
They define what data comes in and goes out of the API.

Schema types:
- Base: Common fields shared across schemas
- Create: Required fields for creating a provider
- Update: Optional fields for updating a provider
- Read: Complete provider data returned to client
"""
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class ProviderBase(BaseModel):
    """
    Base schema with common provider fields.
    Used as parent for other provider schemas.
    """
    name: str = Field(..., min_length=1, max_length=255, description="Provider business name")
    sector: str = Field(..., min_length=1, max_length=100, description="Industry sector (medical, real_estate, etc.)")
    phone: Optional[str] = Field(None, max_length=50, description="Contact phone number")
    email: Optional[EmailStr] = Field(None, description="Contact email address")
    address: Optional[str] = Field(None, description="Physical business address")


class ProviderCreate(ProviderBase):
    """
    Schema for creating a new provider.
    Inherits all required fields from ProviderBase.
    
    Required fields: name, sector
    Optional fields: phone, email, address
    """
    pass


class ProviderUpdate(BaseModel):
    """
    Schema for updating an existing provider.
    ALL fields are optional - only provided fields will be updated.
    
    This allows partial updates (PATCH semantics).
    """
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Updated business name")
    sector: Optional[str] = Field(None, min_length=1, max_length=100, description="Updated sector")
    phone: Optional[str] = Field(None, max_length=50, description="Updated phone number")
    email: Optional[EmailStr] = Field(None, description="Updated email address")
    address: Optional[str] = Field(None, description="Updated address")
    is_active: Optional[bool] = Field(None, description="Whether provider is active")


class ProviderRead(ProviderBase):
    """
    Schema for reading provider data (API response).
    Includes all fields including auto-generated ones.
    
    This is what clients receive when they query providers.
    """
    id: int  # Database ID
    is_active: bool  # Current active status
    created_at: datetime  # When record was created
    updated_at: datetime  # Last time record was updated

    class Config:
        """
        Pydantic configuration.
        from_attributes=True allows creating this schema from ORM models.
        """
        from_attributes = True