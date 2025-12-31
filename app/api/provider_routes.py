"""
Provider API routes - HTTP layer for provider operations.

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
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.provider import ProviderCreate, ProviderUpdate, ProviderRead
from app.repositories.provider_repository import ProviderRepository
from app.services.provider_service import ProviderService

# Create router with prefix and tags for API documentation
router = APIRouter(prefix="/providers", tags=["Providers"])


def get_provider_service(db: Session = Depends(get_db)) -> ProviderService:
    """
    Dependency injection for provider service.
    
    CRITICAL: This is STATELESS.
    - Each request gets a NEW database session via get_db()
    - New repository and service instances are created per request
    - No state persists between requests
    - Session is automatically closed by FastAPI after request
    
    Args:
        db: Database session (injected by FastAPI)
        
    Returns:
        Configured ProviderService ready to use
    """
    repository = ProviderRepository(db)
    return ProviderService(repository)


@router.post("/", response_model=ProviderRead, status_code=201)
def create_provider(
    payload: ProviderCreate,
    service: ProviderService = Depends(get_provider_service)
):
    """
    Create a new provider.
    
    Args:
        payload: Provider data (validated by Pydantic)
        service: Provider service (injected by FastAPI)
        
    Returns:
        Created provider with HTTP 201 status
        
    Raises:
        HTTPException 400: If business rules are violated
        
    Example request body:
        {
            "name": "City Medical Clinic",
            "sector": "medical",
            "phone": "+1234567890",
            "email": "info@citymedical.com",
            "address": "123 Main St"
        }
    """
    try:
        return service.register_provider(payload)
    except ValueError as e:
        # Convert business rule violations to HTTP 400 Bad Request
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[ProviderRead])
def list_providers(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum records to return"),
    sector: Optional[str] = Query(None, description="Filter by sector (e.g., medical, real_estate)"),
    service: ProviderService = Depends(get_provider_service)
):
    """
    List all providers with optional filtering and pagination.
    
    Query parameters:
        - skip: Number of records to skip (default: 0)
        - limit: Max records to return (default: 100, max: 100)
        - sector: Filter by sector (optional)
        
    Returns:
        List of providers matching criteria
        
    Example:
        GET /providers?sector=medical&skip=0&limit=10
    """
    return service.get_providers(skip=skip, limit=limit, sector=sector)


@router.get("/{provider_id}", response_model=ProviderRead)
def get_provider(
    provider_id: int,
    service: ProviderService = Depends(get_provider_service)
):
    """
    Get a specific provider by ID.
    
    Args:
        provider_id: Provider's database ID (from URL path)
        service: Provider service (injected by FastAPI)
        
    Returns:
        Provider details
        
    Raises:
        HTTPException 404: If provider not found
        
    Example:
        GET /providers/1
    """
    try:
        return service.get_provider(provider_id)
    except ValueError as e:
        # Convert "not found" errors to HTTP 404
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/{provider_id}", response_model=ProviderRead)
def update_provider(
    provider_id: int,
    payload: ProviderUpdate,
    service: ProviderService = Depends(get_provider_service)
):
    """
    Update a provider (partial update using PATCH semantics).
    
    Only provided fields will be updated. Omitted fields remain unchanged.
    
    Args:
        provider_id: Provider's database ID (from URL path)
        payload: Fields to update (validated by Pydantic)
        service: Provider service (injected by FastAPI)
        
    Returns:
        Updated provider
        
    Raises:
        HTTPException 404: If provider not found
        
    Example request body (all fields optional):
        {
            "phone": "+9876543210",
            "is_active": false
        }
    """
    try:
        return service.update_provider(provider_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{provider_id}", status_code=204)
def delete_provider(
    provider_id: int,
    service: ProviderService = Depends(get_provider_service)
):
    """
    Delete a provider.
    
    WARNING: This is a hard delete. Consider soft delete (is_active=false) instead.
    
    Args:
        provider_id: Provider's database ID (from URL path)
        service: Provider service (injected by FastAPI)
        
    Returns:
        HTTP 204 No Content (successful deletion returns no body)
        
    Raises:
        HTTPException 404: If provider not found
        
    Example:
        DELETE /providers/1
    """
    try:
        service.delete_provider(provider_id)
        # No return value - HTTP 204 means "success, no content"
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))